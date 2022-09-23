import contextlib
import datetime
import json
import os
import pathlib
import shutil
import string
import uuid
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from substra.sdk import exceptions
from substra.sdk import fs
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.backends.local import dal
from substra.sdk.backends.local.compute import spawner
from substra.sdk.backends.local.compute.spawner import BaseSpawner
from substra.sdk.backends.local.compute.spawner.base import VOLUME_CLI_ARGS
from substra.sdk.backends.local.compute.spawner.base import VOLUME_INPUTS
from substra.sdk.backends.local.compute.spawner.base import VOLUME_OUTPUTS

TPL_VOLUME_INPUTS = "${" + VOLUME_INPUTS + "}"
TPL_VOLUME_OUTPUTS = "${" + VOLUME_OUTPUTS + "}"


class TaskResource(dict):
    def __init__(self, id: str, value: str, multiple: bool):
        super().__init__(self, id=id, value=value, multiple=multiple)


class Filenames(str, Enum):
    OPENER = "opener.py"  # The name must end in .py for substra-tools module loading


def _mkdir(path, delete_if_exists=False):
    """Make directory (recursive)."""
    path = Path(path)
    if path.exists():
        if not delete_if_exists:
            return path
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def _generate_filename():
    return str(uuid.uuid4())


class Worker:
    """ML Worker."""

    def __init__(
        self,
        db: dal.DataAccess,
        local_worker_dir: pathlib.Path,
        debug_spawner: Type[BaseSpawner],
    ):
        self._local_worker_dir = local_worker_dir
        self._db = db
        self._spawner = spawner.get(name=debug_spawner, local_worker_dir=self._local_worker_dir)

    @contextlib.contextmanager
    def _context(self, key):
        try:
            tmp_dir = _mkdir(os.path.join(self._local_worker_dir, key))
            yield Path(tmp_dir)
        finally:
            # delete task working directory
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _save_cp_performances_as_json(self, compute_plan_key: str, path: Path):
        """Dump a json file containing the performances of the given compute plan in the given path."""

        performances = self._db.get_performances(compute_plan_key)

        with (path).open("w", encoding="UTF-8") as json_file:
            json.dump(performances.dict(), json_file, default=str)

    def _get_asset_unknown_type(self, asset_key, possible_types: List[schemas.Type]) -> Tuple[Any, schemas.Type]:
        for asset_type in possible_types:
            try:
                asset = self._db.get(asset_type, asset_key)
                break
            except exceptions.NotFound:
                pass
        if asset is None:
            raise exceptions.NotFound(f"Wrong pk {asset_key}", 404)
        return asset, asset_type

    def _update_cp(self, compute_plan: models.ComputePlan, update_live_performances: bool):
        compute_plan.done_count += 1
        compute_plan.todo_count -= 1
        if compute_plan.done_count == compute_plan.task_count:
            compute_plan.status = models.ComputePlanStatus.done
            compute_plan.end_date = datetime.datetime.now()
            compute_plan.estimated_end_date = compute_plan.end_date

            compute_plan.duration = int((compute_plan.end_date - compute_plan.start_date).total_seconds())

        # save live performances
        if update_live_performances:
            live_perf_path = Path(self._local_worker_dir / "live_performances" / compute_plan.key / "performances.json")
            _mkdir(live_perf_path.parent)
            self._save_cp_performances_as_json(compute_plan.key, live_perf_path)

    def _get_cmd_template_inputs_outputs(
        self,
        task,
        cmd_line_inputs,
        output_id_filename,
    ):
        command_template = ["--rank", task.rank]

        cmd_line_outputs: List[TaskResource] = [
            TaskResource(id=output_id, value=f"{TPL_VOLUME_OUTPUTS}/{filename}", multiple=False)
            for output_id, filename in output_id_filename.items()
        ]

        command_template += [
            "--inputs",
            json.dumps(cmd_line_inputs, default=str),
            "--outputs",
            json.dumps(cmd_line_outputs, default=str),
        ]
        return command_template

    def _prepare_artifact_input(self, task_input, input_volume, multiple):
        in_task, _ = self._get_asset_unknown_type(
            asset_key=task_input.parent_task_key,
            possible_types=[
                schemas.Type.Aggregatetuple,
                schemas.Type.CompositeTraintuple,
                schemas.Type.Predicttuple,
                schemas.Type.Testtuple,
                schemas.Type.Traintuple,
            ],
        )
        input_artifact = in_task.outputs[task_input.parent_task_output_identifier].value
        assert isinstance(
            input_artifact, models.OutModel
        ), "The task_input value must be an artifact, not a performance"
        filename = _generate_filename()
        path_to_input = input_volume / filename
        Path(input_artifact.address.storage_address).link_to(path_to_input)

        return TaskResource(id=task_input.identifier, value=f"{TPL_VOLUME_INPUTS}/{filename}", multiple=multiple)

    def _prepare_dataset_input(
        self, dataset: models.Dataset, task_input: models.InputRef, input_volume: str, multiple: bool
    ):
        path_to_opener = input_volume / Filenames.OPENER.value
        Path(dataset.opener.storage_address).link_to(path_to_opener)
        return TaskResource(
            id=task_input.identifier,
            value=f"{TPL_VOLUME_INPUTS}/{Filenames.OPENER.value}",
            multiple=multiple,
        )

    def _prepare_datasample_input(
        self, datasample_input_refs: List[models.InputRef], datasamples: List[models.DataSample], multiple: bool
    ) -> Tuple[List[TaskResource], Dict[str, str]]:
        task_resources = list()
        data_sample_paths = dict()
        for datasample_input, datasample in zip(datasample_input_refs, datasamples):
            datasample_path_arg = f"{TPL_VOLUME_INPUTS}/{datasample_input.asset_key}"
            task_resources.append(
                TaskResource(id=datasample_input.identifier, value=str(datasample_path_arg), multiple=multiple)
            )
            data_sample_paths[datasample.key] = datasample.path
        return task_resources, data_sample_paths

    def _prepare_datasamples_inputs_and_paths(
        self,
        task,
        dataset: models.Dataset,
        datasamples: List[models.DataSample],
        datasample_input_refs: List[models.InputRef],
        multiple: bool,
    ) -> Tuple[str, List[TaskResource], Optional[Dict[str, str]]]:
        command_template = []
        datasample_task_resources = []
        data_sample_paths = None

        if len(datasamples) == 0:
            pass
        elif dataset is not None and not self._db.is_local(dataset.key, schemas.Type.Dataset):
            # Hybrid mode
            command_template += ["--fake-data"]
            command_template += ["--n-fake-samples", len(datasample_input_refs)]
        else:
            datasample_task_resources, data_sample_paths = self._prepare_datasample_input(
                datasample_input_refs=datasample_input_refs, datasamples=datasamples, multiple=multiple
            )

        return command_template, datasample_task_resources, data_sample_paths

    def _update_deprecated_fields(self, task, value: Union[float, models.OutModel], algo_key: str):
        if isinstance(task, models.Aggregatetuple):
            task.aggregate.models = [value]
        elif isinstance(task, models.CompositeTraintuple):
            if task.composite.models is None:
                task.composite.models = list()
            task.composite.models.append(value)
        elif isinstance(task, models.Predicttuple):
            task.predict.models = [value]
        elif isinstance(task, models.Testtuple):
            task.test.perfs[algo_key] = value
        elif isinstance(task, models.Traintuple):
            task.train.models = [value]
        else:
            raise ValueError(f"Unsupported type of task {type(task)}")

    def _save_output(
        self,
        task,
        algo_output: models.AlgoOutput,
        output_id_filename: Dict[str, str],
        output_volume: str,
        algo_key: str,
    ) -> bool:
        update_live_performances = False
        if algo_output.multiple:
            raise NotImplementedError("Multiple output value is not supported yet.")
        filename = output_id_filename[algo_output.identifier]
        tmp_path = output_volume / filename
        output_dir = _mkdir(self._local_worker_dir / "outputs" / task.key)
        output_path = output_dir / filename
        shutil.copy(tmp_path, output_path)

        if algo_output.kind == schemas.AssetKind.performance:
            update_live_performances = True
            perf = json.loads(output_path.read_text())["all"]
            task.outputs[algo_output.identifier].value = perf
            value = perf
        elif algo_output.kind == schemas.AssetKind.model:
            value = models.OutModel(
                key=str(uuid.uuid4()),
                compute_task_key=task.key,
                address=models.InModel(
                    checksum=fs.hash_file(output_path),
                    storage_address=output_path,
                ),
                creation_date=datetime.datetime.now(),
                owner=task.owner,
                permissions=task.outputs[algo_output.identifier].permissions,
            )
            task.outputs[algo_output.identifier].value = value
            self._db.add(value)

        else:
            raise ValueError(f"This asset kind is not supported for algo output: {algo_output.kind}")

        self._update_deprecated_fields(task=task, value=value, algo_key=algo_key)
        return update_live_performances

    def schedule_task(self, task: models._GenericTraintuple):
        """Execute the task

        Args:
            task: Task to execute
        """
        with self._context(task.key) as task_dir:

            task.status = models.Status.doing
            task.start_date = datetime.datetime.now()

            algo = self._db.get_with_files(schemas.Type.Algo, task.algo.key)
            input_multiplicity = {i.identifier: i.multiple for i in algo.inputs}
            compute_plan = self._db.get(schemas.Type.ComputePlan, task.compute_plan_key)

            command_template = []

            volumes = {
                VOLUME_INPUTS: _mkdir(task_dir / "inputs"),
                VOLUME_OUTPUTS: _mkdir(task_dir / "outputs"),
                VOLUME_CLI_ARGS: _mkdir(task_dir / "cli-args"),
            }

            cmd_line_inputs: List[TaskResource] = []

            dataset: Optional[models.Dataset] = None
            data_sample_paths: Optional[Dict[str, str]] = None

            datasample_input_refs: List[models.InputRef] = list()
            datasamples: List[models.DataSample] = list()

            # Prepare inputs
            for task_input in task.inputs:
                multiple = input_multiplicity[task_input.identifier]

                if task_input.parent_task_key is not None:
                    task_resource = self._prepare_artifact_input(
                        task_input=task_input,
                        input_volume=volumes[VOLUME_INPUTS],
                        multiple=multiple,
                    )
                    cmd_line_inputs.append(task_resource)
                else:
                    asset, asset_type = self._get_asset_unknown_type(
                        asset_key=task_input.asset_key, possible_types=[schemas.Type.DataSample, schemas.Type.Dataset]
                    )
                    if asset_type == schemas.Type.DataSample:
                        # This is necessary because of the hybrid mode
                        # Otherwise could process the task_input here
                        datasample_input_refs.append(task_input)
                        datasamples.append(asset)
                    elif asset_type == schemas.Type.Dataset:
                        dataset = self._db.get_with_files(schemas.Type.Dataset, task_input.asset_key)
                        cmd_line_inputs.append(
                            self._prepare_dataset_input(
                                dataset=dataset,
                                task_input=task_input,
                                input_volume=volumes[VOLUME_INPUTS],
                                multiple=multiple,
                            )
                        )

            (
                datasample_cmd_template,
                datasample_task_resources,
                data_sample_paths,
            ) = self._prepare_datasamples_inputs_and_paths(
                task=task,
                dataset=dataset,
                datasamples=datasamples,
                datasample_input_refs=datasample_input_refs,
                multiple=input_multiplicity.get(schemas.StaticInputIdentifier.datasamples),
            )
            command_template += datasample_cmd_template
            cmd_line_inputs.extend(datasample_task_resources)

            # Prepare the outputs
            output_id_filename: Dict[str, str] = {output_id: _generate_filename() for output_id in task.outputs}

            command_template += self._get_cmd_template_inputs_outputs(
                task=task,
                cmd_line_inputs=cmd_line_inputs,
                output_id_filename=output_id_filename,
            )
            command_template += ["--log-level", "warning"]

            # Task execution
            container_name = f"algo-{algo.algorithm.checksum}"
            self._spawner.spawn(
                container_name,
                str(algo.algorithm.storage_address),
                command_args_tpl=[string.Template(str(part)) for part in command_template],
                local_volumes=volumes,
                data_sample_paths=data_sample_paths,
                envs=None,
            )

            # Save the outputs
            update_live_performances = False
            for algo_output in algo.outputs:
                update_live_performances = self._save_output(
                    task=task,
                    algo_output=algo_output,
                    output_id_filename=output_id_filename,
                    output_volume=volumes[VOLUME_OUTPUTS],
                    algo_key=algo.key,
                )

            # Set status
            task.status = models.Status.done
            task.end_date = datetime.datetime.now()

            self._update_cp(compute_plan=compute_plan, update_live_performances=update_live_performances)
