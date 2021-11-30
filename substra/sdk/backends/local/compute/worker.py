# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import contextlib
import json
import os
import pathlib
import shutil
import string
import typing
import uuid
import datetime
from enum import Enum

from substra.sdk import schemas, fs, models, exceptions
from substra.sdk.backends.local import dal
from substra.sdk.backends.local.compute import spawner
from substra.sdk.backends.local.compute.spawner import DEBUG_SPAWNER_CHOICES, BaseSpawner


class Filenames(str, Enum):
    OUT_MODEL = "out-model"
    OUT_HEAD_MODEL = "out-head-model"
    OUT_TRUNK_MODEL = "out-trunk-model"
    PREDICTIONS = "pred"
    PERFORMANCE = "perf.json"


def _mkdir(path, delete_if_exists=False):
    """Make directory (recursive)."""
    if os.path.exists(path):
        if not delete_if_exists:
            return path
        shutil.rmtree(path)
    os.makedirs(path)
    return path


def _get_address_in_container(model_key, volume, container_volume):
    return pathlib.Path(os.path.join(volume, model_key).replace(volume, container_volume))


class Worker:
    """ML Worker."""

    def __init__(
        self,
        db: dal.DataAccess,
        local_worker_dir: pathlib.Path,
        support_chainkeys: bool,
        debug_spawner: typing.Type[BaseSpawner] = DEBUG_SPAWNER_CHOICES['docker'],
        chainkey_dir=None,
    ):
        self._local_worker_dir = local_worker_dir
        self._db = db
        self._spawner = spawner.get(name=debug_spawner, local_worker_dir=self._local_worker_dir)
        self._support_chainkeys = support_chainkeys
        self._chainkey_dir = chainkey_dir

    def _has_chainkey(self):
        # checks if chainkey exists in the chainkey_dir
        return os.path.exists(self._chainkey_dir / "node_name_id.json")

    def _get_chainkey_volume(self, tuple_):
        compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_key)
        tuple_chainkey_volume = self._chainkey_dir / tuple_.worker / \
            "computeplan" / compute_plan.tag / "chainkeys"
        if not tuple_chainkey_volume.is_dir():
            return None
        return tuple_chainkey_volume

    def _get_chainkey_env(self, tuple_):
        node_name_id = json.loads((self._chainkey_dir / "node_name_id.json").read_text())
        return {
            'NODE_INDEX': str(node_name_id.get(tuple_.worker, None)),
        }

    def _get_data_sample_paths_arg(self, data_volume, data_sample_keys):
        data_sample_paths = [
            os.path.join(data_volume, key)
            for key in data_sample_keys
        ]
        data_sample_paths = ' '.join(data_sample_paths)
        return data_sample_paths

    def _get_data_volume(self, tuple_dir, tuple_):
        data_volume = _mkdir(os.path.join(tuple_dir, "data"))
        if isinstance(tuple_, models.Traintuple):
            data_sample_keys = tuple_.train.data_sample_keys
        elif isinstance(tuple_, models.CompositeTraintuple):
            data_sample_keys = tuple_.composite.data_sample_keys
        elif isinstance(tuple_, models.Testtuple):
            data_sample_keys = tuple_.test.data_sample_keys
        samples = [
            self._db.get(schemas.Type.DataSample, key) for key in data_sample_keys
        ]
        for sample in samples:
            # TODO more efficient link (symlink?)
            shutil.copytree(sample.path, os.path.join(data_volume, sample.key))
        return data_volume

    def _save_output_model(self, tuple_, model_name, models_volume, permissions) -> models.OutModel:
        if model_name == Filenames.OUT_HEAD_MODEL:
            category = models.ModelType.head
        elif model_name == Filenames.OUT_TRUNK_MODEL:
            category = models.ModelType.simple
        elif model_name == Filenames.OUT_MODEL:
            category = models.ModelType.simple
        else:
            raise Exception(f"TODO write - Unknown model name {model_name}")

        tmp_path = os.path.join(models_volume, model_name)
        model_dir = _mkdir(os.path.join(self._local_worker_dir, "models", tuple_.key))
        model_path = os.path.join(model_dir, model_name)
        shutil.copy(tmp_path, model_path)

        return models.OutModel(
            key=uuid.uuid4().hex,
            category=category,
            compute_task_key=tuple_.key,
            address=models.InModel(
                checksum=fs.hash_file(model_path),
                storage_address=model_path,
            ),
            creation_date=datetime.datetime.now(),
            owner=tuple_.worker,    # TODO: check this
            permissions=permissions,    # TODO: check this
        )

    @contextlib.contextmanager
    def _context(self, key):
        try:
            tmp_dir = _mkdir(os.path.join(self._local_worker_dir, key))
            yield tmp_dir
        finally:
            # delete tuple working directory
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def schedule_traintuple(self, tuple_):
        """Schedules a ML task (blocking)."""
        with self._context(tuple_.key) as tuple_dir:
            tuple_.status = models.Status.doing
            tuple_.start_date = datetime.datetime.now()

            # fetch dependencies
            algo = self._db.get_with_files(schemas.Type.Algo, tuple_.algo.key)

            compute_plan = None
            if tuple_.compute_plan_key:
                compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_key)

            volumes = dict()

            if isinstance(tuple_, models.Aggregatetuple):
                command_template = "aggregate"
            else:
                command_template = "train"
                command_template += " --opener-path ${_VOLUME_OPENER}"

            # Prepare input models
            in_tuples = list()
            if tuple_.parent_task_keys is not None and len(tuple_.parent_task_keys) > 0:
                for in_tuple_key in tuple_.parent_task_keys:
                    in_tuple = None
                    for tuple_type in [
                        schemas.Type.Traintuple,
                        schemas.Type.CompositeTraintuple,
                        schemas.Type.Aggregatetuple
                    ]:
                        try:
                            in_tuple = self._db.get(tuple_type, in_tuple_key)
                            break
                        except exceptions.NotFound:
                            pass
                    if in_tuple is None:
                        raise exceptions.NotFound(f"Wrong pk {in_tuple_key}", 404)

                    if in_tuple not in in_tuples:
                        in_tuples.append(in_tuple)

            # The in models command is a nargs+, so we have to append it to the
            # command template later
            in_models_command_template = ''

            input_models_volume = _mkdir(os.path.join(tuple_dir, "input_models"))
            volumes['_VOLUME_INPUT_MODELS'] = input_models_volume

            if isinstance(tuple_, models.CompositeTraintuple):
                assert len(in_tuples) <= 2

                for in_tuple in in_tuples:
                    if isinstance(in_tuple, models.CompositeTraintuple):
                        input_models = [m for m in in_tuple.composite.models
                                        if m.category == models.ModelType.head]
                        assert len(input_models) == 1, f'Unavailable input model {input_models}'
                        input_model = input_models[0]

                        os.link(
                            input_model.address.storage_address,
                            os.path.join(input_models_volume, "input_head_model")
                        )
                        head_model_container_address = _get_address_in_container(
                            "input_head_model",
                            input_models_volume,
                            "${_VOLUME_INPUT_MODELS}",
                        )
                        in_models_command_template += f' --input-head-model-filename \
                            {head_model_container_address}'

                        if len(in_tuples) == 1:  # No other trunk
                            input_models = [m for m in in_tuple.composite.models
                                            if m.category == models.ModelType.simple]
                            assert len(input_models) == 1, f'Unavailable input model {input_models}'
                            input_model = input_models[0]
                            os.link(
                                input_model.address.storage_address,
                                os.path.join(input_models_volume, "input_trunk_model")
                            )
                            trunk_model_container_address = _get_address_in_container(
                                "input_trunk_model",
                                input_models_volume,
                                "${_VOLUME_INPUT_MODELS}",
                            )
                            in_models_command_template += f' --input-trunk-model-filename \
                                {trunk_model_container_address}'
                    elif isinstance(in_tuple, models.Aggregatetuple):
                        assert in_tuple.aggregate.models is not None \
                            and len(in_tuple.aggregate.models) == 1
                        input_model = in_tuple.aggregate.models[0]

                        os.link(
                            input_model.address.storage_address,
                            os.path.join(input_models_volume, "input_trunk_model")
                        )
                        trunk_model_container_address = _get_address_in_container(
                            "input_trunk_model",
                            input_models_volume,
                            "${_VOLUME_INPUT_MODELS}",
                        )
                        in_models_command_template += f' --input-trunk-model-filename \
                            {trunk_model_container_address}'
                    else:
                        raise Exception('TODO write this - cannot link traintuple to composite')

            else:
                # The tuple is a traintuple or an aggregate traintuple
                in_models_command_template += ' --models-path ${_VOLUME_INPUT_MODELS}'
                for idx, in_tuple in enumerate(in_tuples):
                    if isinstance(in_tuple, models.CompositeTraintuple):
                        input_models = [m for m in in_tuple.composite.models
                                        if m.category == models.ModelType.simple]
                        assert len(input_models) == 1, f'Unavailable input model {input_models}'
                        input_model = input_models[0]
                    elif isinstance(in_tuple, models.Traintuple):
                        assert in_tuple.train.models is not None \
                            and len(in_tuple.train.models) == 1
                        input_model = in_tuple.train.models[0]
                    elif isinstance(in_tuple, models.Aggregatetuple):
                        assert in_tuple.aggregate.models is not None \
                            and len(in_tuple.aggregate.models) == 1
                        input_model = in_tuple.aggregate.models[0]
                    else:
                        raise Exception(f'TODO write this - unknown input model type {in_tuple}')

                    model_filename = f"{idx}_{input_model.key}"
                    os.link(
                        input_model.address.storage_address,
                        os.path.join(input_models_volume, model_filename)
                    )
                    in_models_command_template += f" {model_filename}"

            # Prepare the out model command
            output_models_volume = _mkdir(os.path.join(tuple_dir, "output_models"))
            volumes['_VOLUME_OUTPUT_MODELS'] = output_models_volume

            if isinstance(tuple_, models.CompositeTraintuple):
                command_template += ' --output-models-path ${_VOLUME_OUTPUT_MODELS}'
                command_template += f' --output-head-model-filename {Filenames.OUT_HEAD_MODEL}'
                command_template += f' --output-trunk-model-filename {Filenames.OUT_TRUNK_MODEL}'
            else:
                command_template += ' --output-model-path ${_VOLUME_OUTPUT_MODELS}/' \
                    f'{Filenames.OUT_MODEL}'

            # Prepare the data
            if not isinstance(tuple_, models.Aggregatetuple):
                # if this is a traintuple or composite traintuple, prepare the data
                if isinstance(tuple_, models.Traintuple):
                    dataset_key = tuple_.train.data_manager_key
                    train_data_sample_keys = tuple_.train.data_sample_keys
                if isinstance(tuple_, models.CompositeTraintuple):
                    dataset_key = tuple_.composite.data_manager_key
                    train_data_sample_keys = tuple_.composite.data_sample_keys

                dataset = self._db.get_with_files(schemas.Type.Dataset, dataset_key)
                volumes['_VOLUME_OPENER'] = dataset.opener.storage_address
                if self._db.is_local(dataset_key, schemas.Type.Dataset):
                    data_volume = self._get_data_volume(tuple_dir, tuple_)
                    volumes['_VOLUME_INPUT_DATASAMPLES'] = data_volume
                    data_sample_paths = self._get_data_sample_paths_arg(
                        "${_VOLUME_INPUT_DATASAMPLES}",
                        train_data_sample_keys,
                    )
                    command_template += f" --data-sample-paths {data_sample_paths}"
                else:
                    command_template += " --fake-data"
                    command_template += f" --n-fake-samples {len(dataset.train_data_sample_keys)}"

            # Prepare the shared compute plan volume
            if tuple_.compute_plan_key:
                local_volume = _mkdir(
                    os.path.join(
                        self._local_worker_dir, "compute_plans", tuple_.worker,
                        tuple_.compute_plan_key
                    )
                )
                volumes['_VOLUME_LOCAL'] = local_volume
                command_template += " --compute-plan-path ${_VOLUME_LOCAL}"
                if self._support_chainkeys and self._has_chainkey():
                    chainkey_volume = self._get_chainkey_volume(tuple_)
                    if chainkey_volume is not None:
                        volumes['_VOLUME_CHAINKEYS'] = chainkey_volume
                        command_template += " --chainkeys-path ${_VOLUME_CHAINKEYS}"

            command_template += f" --rank {tuple_.rank}"

            # Add the in_models to the command_template
            command_template += in_models_command_template

            # Get the environment variables
            envs = dict()
            if tuple_.compute_plan_key:
                if self._support_chainkeys and self._has_chainkey():
                    envs.update(self._get_chainkey_env(tuple_))

            # Execute the tuple
            container_name = f"algo-{algo.algorithm.checksum}"
            self._spawner.spawn(
                container_name,
                str(algo.algorithm.storage_address),
                command_template=string.Template(command_template),
                local_volumes=volumes,
                envs=envs,
            )

            # save move output models
            if isinstance(tuple_, models.CompositeTraintuple):
                head_model = self._save_output_model(
                    tuple_,
                    Filenames.OUT_HEAD_MODEL,
                    output_models_volume,
                    permissions=tuple_.composite.head_permissions
                )
                trunk_model = self._save_output_model(
                    tuple_,
                    Filenames.OUT_TRUNK_MODEL,
                    output_models_volume,
                    permissions=tuple_.composite.trunk_permissions
                )
                tuple_.composite.models = [head_model, trunk_model]
            elif isinstance(tuple_, models.Traintuple):
                out_model = self._save_output_model(
                    tuple_, Filenames.OUT_MODEL,
                    output_models_volume, tuple_.train.model_permissions)
                tuple_.train.models = [out_model]
            elif isinstance(tuple_, models.Aggregatetuple):
                out_model = self._save_output_model(
                    tuple_, Filenames.OUT_MODEL,
                    output_models_volume, tuple_.aggregate.model_permissions)
                tuple_.aggregate.models = [out_model]

            # set status
            tuple_.status = models.Status.done
            tuple_.end_date = datetime.datetime.now()

            if tuple_.compute_plan_key:
                compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_key)
                compute_plan.done_count += 1
                compute_plan.todo_count -= 1
                if compute_plan.done_count == compute_plan.task_count:
                    compute_plan.status = models.ComputePlanStatus.done
                    compute_plan.end_date = datetime.datetime.now()
                    compute_plan.estimated_end_date = compute_plan.end_date

                    compute_plan.duration = int((compute_plan.end_date -
                                                 compute_plan.start_date).total_seconds())

    def schedule_testtuple(self, tuple_):
        """Schedules a ML task (blocking)."""
        with self._context(tuple_.key) as tuple_dir:
            tuple_.status = models.Status.doing
            tuple_.start_date = datetime.datetime.now()

            # fetch dependencies
            assert len(tuple_.parent_task_keys) == 1
            traintuple = None
            for traintuple_type in [
                schemas.Type.Traintuple,
                schemas.Type.CompositeTraintuple,
                schemas.Type.Aggregatetuple,
            ]:
                try:
                    traintuple = self._db.get(traintuple_type, tuple_.parent_task_keys[0])
                    break
                except exceptions.NotFound:
                    pass
            if traintuple is None:
                raise exceptions.NotFound(f"Wrong pk {tuple_.parent_task_keys[0]}", 404)

            algo = self._db.get_with_files(schemas.Type.Algo, tuple_.algo.key)
            metrics = [
                self._db.get_with_files(schemas.Type.Metric, metric_key)
                for metric_key in tuple_.test.metric_keys
            ]
            dataset = self._db.get_with_files(schemas.Type.Dataset, tuple_.test.data_manager_key)

            compute_plan = None
            if tuple_.compute_plan_key:
                compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_key)

            # prepare model and datasamples
            predictions_volume = _mkdir(os.path.join(tuple_dir, "pred"))
            models_volume = _mkdir(os.path.join(tuple_dir, "models"))
            performance_volume = _mkdir(os.path.join(tuple_dir, "perf"))

            volumes = {
                '_VOLUME_OPENER': dataset.opener.storage_address,
                '_VOLUME_INPUT_MODELS': models_volume,
                '_VOLUME_OUTPUT_PRED': predictions_volume,
            }

            # If use fake data, no data volume
            if self._db.is_local(dataset.key, schemas.Type.Dataset):
                data_volume = self._get_data_volume(tuple_dir, tuple_)
                volumes['_VOLUME_INPUT_DATASAMPLES'] = data_volume

            # compute testtuple command_template
            command_template = "predict"

            if tuple_.compute_plan_key:
                local_volume = _mkdir(
                    os.path.join(
                        self._local_worker_dir, "compute_plans", tuple_.worker,
                        tuple_.compute_plan_key
                    )
                )
                volumes['_VOLUME_LOCAL'] = local_volume
                command_template += " --compute-plan-path ${_VOLUME_LOCAL}"
                if self._support_chainkeys and self._has_chainkey():
                    chainkey_volume = self._get_chainkey_volume(tuple_)
                    volumes['_VOLUME_CHAINKEYS'] = chainkey_volume
                    command_template += " --chainkeys-path ${_VOLUME_CHAINKEYS}"

            if isinstance(traintuple, models.Traintuple):
                assert traintuple.train.models is not None and len(traintuple.train.models) == 1
                in_testtuple_model = traintuple.train.models[0]
                os.link(
                    in_testtuple_model.address.storage_address,
                    os.path.join(models_volume, in_testtuple_model.key),
                )
                model_container_address = _get_address_in_container(
                    in_testtuple_model.key,
                    models_volume,
                    "${_VOLUME_INPUT_MODELS}"
                )
                command_template += f" {model_container_address}"

            elif isinstance(traintuple, models.Aggregatetuple):
                assert traintuple.aggregate.models is not None \
                    and len(traintuple.aggregate.models) == 1
                in_testtuple_model = traintuple.aggregate.models[0]
                os.link(
                    in_testtuple_model.address.storage_address,
                    os.path.join(models_volume, in_testtuple_model.key),
                )
                model_container_address = _get_address_in_container(
                    in_testtuple_model.key,
                    models_volume,
                    "${_VOLUME_INPUT_MODELS}"
                )
                command_template += f" {model_container_address}"

            elif isinstance(traintuple, models.CompositeTraintuple):
                assert traintuple.composite.models is not None \
                    and len(traintuple.composite.models) == 2
                for in_testtuple_model in traintuple.composite.models:
                    os.link(
                        in_testtuple_model.address.storage_address,
                        os.path.join(models_volume, in_testtuple_model.key),
                    )
                    address_in_container = _get_address_in_container(
                        in_testtuple_model.key,
                        models_volume,
                        "${_VOLUME_INPUT_MODELS}",
                    )
                    if in_testtuple_model.category == models.ModelType.head:
                        command_name = ' --input-head-model-filename'
                    elif in_testtuple_model.category == models.ModelType.simple:
                        command_name = ' --input-trunk-model-filename'
                    command_template += f" {command_name} {address_in_container}"

            if self._db.is_local(dataset.key, schemas.Type.Dataset):
                data_sample_paths = self._get_data_sample_paths_arg(
                    "${_VOLUME_INPUT_DATASAMPLES}",
                    tuple_.test.data_sample_keys,
                )
                command_template += f" --data-sample-paths {data_sample_paths}"
            else:
                command_template += " --fake-data"
                command_template += f" --n-fake-samples {len(tuple_.test.data_sample_keys)}"

            command_template += " --opener-path ${_VOLUME_OPENER}"
            command_template += " --output-predictions-path ${_VOLUME_OUTPUT_PRED}" \
                f"/{Filenames.PREDICTIONS}"

            container_name = f"algo-{algo.algorithm.checksum}"
            self._spawner.spawn(
                name=container_name,
                archive_path=str(algo.algorithm.storage_address),
                command_template=string.Template(command_template),
                local_volumes=volumes,
            )

            # Calculate the metrics
            for metric in metrics:
                volumes = {
                    "_VOLUME_OUTPUT_PRED": predictions_volume,
                    "_VOLUME_OPENER": dataset.opener.storage_address,
                    "_VOLUME_OUTPUT_PERF": performance_volume,
                }

                if self._db.is_local(dataset.key, schemas.Type.Dataset):
                    data_sample_paths = self._get_data_sample_paths_arg(
                        "${_VOLUME_INPUT_DATASAMPLES}",
                        tuple_.test.data_sample_keys,
                    )
                    volumes["_VOLUME_INPUT_DATASAMPLES"] = data_volume
                    command_template = " --fake-data-mode DISABLED"
                    command_template += f" --data-sample-paths {data_sample_paths}"
                else:
                    command_template = " --fake-data-mode FAKE_Y"
                    command_template += f" --n-fake-samples {len(tuple_.test.data_sample_keys)}"

                command_template += " --opener-path ${_VOLUME_OPENER}"
                command_template += " --input-predictions-path ${_VOLUME_OUTPUT_PRED}" \
                    f"/{Filenames.PREDICTIONS}"
                command_template += " --output-perf-path ${_VOLUME_OUTPUT_PERF}" \
                    f"/{Filenames.PERFORMANCE}"

                container_name = f'metrics-{metric.address.checksum}'
                self._spawner.spawn(
                    container_name,
                    str(metric.address.storage_address),
                    command_template=string.Template(command_template),
                    local_volumes=volumes,
                )

                # save move performance
                tmp_path = os.path.join(performance_volume, Filenames.PERFORMANCE)
                pred_dir = _mkdir(os.path.join(self._local_worker_dir, "performances", tuple_.key))
                pred_path = os.path.join(pred_dir, f"performance_{metric.key}.json")
                shutil.copy(tmp_path, pred_path)

                with open(pred_path, 'r') as f:
                    tuple_.test.perfs[metric.key] = json.load(f).get('all')

            # set status
            tuple_.status = models.Status.done
            tuple_.end_date = datetime.datetime.now()

            if compute_plan:
                compute_plan.done_count += 1
                compute_plan.todo_count -= 1
                if compute_plan.done_count == compute_plan.task_count:
                    compute_plan.status = models.ComputePlanStatus.done
                    compute_plan.end_date = datetime.datetime.now()
                    compute_plan.estimated_end_date = compute_plan.end_date
                    compute_plan.duration = int((compute_plan.end_date -
                                                 compute_plan.start_date).total_seconds())
