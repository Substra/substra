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

from substra.sdk import schemas
from substra.runner import METRICS_NO_FAKE_Y, DOCKER_METRICS_TAG
from substra.sdk.backends.local import db
from substra.sdk.backends.local import models
from substra.sdk.backends.local import fs
from substra.sdk.backends.local.compute import spawner

_CONTAINER_MODEL_PATH = "/sandbox/model"

_VOLUME_INPUT_DATASAMPLES = {"bind": "/sandbox/data", "mode": "ro"}
_VOLUME_MODELS_RO = {"bind": _CONTAINER_MODEL_PATH, "mode": "ro"}
_VOLUME_MODELS_RW = {"bind": _CONTAINER_MODEL_PATH, "mode": "rw"}
_VOLUME_OPENER = {"bind": "/sandbox/opener/__init__.py", "mode": "ro"}
_VOLUME_OUTPUT_PRED = {"bind": "/sandbox/pred", "mode": "rw"}
_VOLUME_LOCAL = {"bind": "/sandbox/local", "mode": "rw"}
_VOLUME_LOCAL_READ_ONLY = {"bind": "/sandbox/local", "mode": "ro"}


def _mkdir(path, delete_if_exists=False):
    """Make directory (recursive)."""
    if os.path.exists(path):
        if not delete_if_exists:
            return path
        shutil.rmtree(path)
    os.makedirs(path)
    return path


class Worker:
    """ML Worker."""

    def __init__(self):
        self._wdir = os.path.join(os.getcwd(), "local-worker")
        self._db = db.get()
        self._spawner = spawner.get()

    def _get_data_volume(self, tuple_dir, tuple_):
        data_volume = _mkdir(os.path.join(tuple_dir, "data"))
        samples = [
            self._db.get(schemas.Type.DataSample, key) for key in tuple_.dataset.keys
        ]
        for sample in samples:
            # TODO more efficient link (symlink?)
            shutil.copytree(sample.path, os.path.join(data_volume, sample.key))
        return data_volume

    @contextlib.contextmanager
    def _context(self, key):
        try:
            tmp_dir = _mkdir(os.path.join(self._wdir, key))
            yield tmp_dir
        finally:
            # delete tuple working directory
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def schedule_traintuple(self, tuple_):
        """Schedules a ML task (blocking)."""
        # TODO handle all tuple types
        # TODO create a schedule context to clean everything
        with self._context(tuple_.key) as tuple_dir:
            tuple_.status = models.Status.doing

            # fetch dependencies
            algo = self._db.get(schemas.Type.Algo, tuple_.algo_key)
            dataset = self._db.get(schemas.Type.Dataset, tuple_.dataset.key)
            compute_plan = None
            if tuple_.compute_plan_id:
                compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_id)

            # prepare input models and datasamples
            models_volume = _mkdir(os.path.join(tuple_dir, "models"))
            for model in tuple_.in_models:
                os.link(model.storage_address, os.path.join(models_volume, model.key))

            data_volume = self._get_data_volume(tuple_dir, tuple_)

            volumes = {
                dataset.data_opener: _VOLUME_OPENER,
                data_volume: _VOLUME_INPUT_DATASAMPLES,
                models_volume: _VOLUME_MODELS_RW,
            }

            if tuple_.compute_plan_id:
                local_volume = _mkdir(
                    os.path.join(
                        self._wdir, "compute_plans", "local", tuple_.compute_plan_id
                    )
                )
                volumes[local_volume] = _VOLUME_LOCAL

            # compute traintuple command
            command = f"train --rank {tuple_.rank}"
            for model in tuple_.in_models:
                command += f" {model.key}"

            container_name = f"algo-{algo.key}"
            logs = self._spawner.spawn(
                container_name, str(algo.file), command, volumes=volumes
            )

            # save move output models
            tmp_path = os.path.join(models_volume, "model")
            model_dir = _mkdir(os.path.join(self._wdir, "models", tuple_.key))
            model_path = os.path.join(model_dir, "model")
            shutil.copy(tmp_path, model_path)

            # set logs and status
            tuple_.log = "\n".join(logs)
            tuple_.status = models.Status.done
            tuple_.out_model = models.OutModel(
                hash=fs.hash_file(model_path), storage_address=model_path,
            )

            if compute_plan:
                compute_plan.done_count += 1
                if compute_plan.done_count == compute_plan.tuple_count:
                    compute_plan.status = models.Status.done

    def schedule_testtuple(self, tuple_):
        """Schedules a ML task (blocking)."""
        # TODO see if merge with the schedule_traintuple function
        with self._context(tuple_.key) as tuple_dir:
            tuple_.status = models.Status.doing

            # fetch dependencies
            traintuple = self._db.get(schemas.Type.Traintuple, tuple_.traintuple_key)
            algo = self._db.get(schemas.Type.Algo, traintuple.algo_key)
            objective = self._db.get(schemas.Type.Objective, tuple_.objective_key)
            dataset = self._db.get(schemas.Type.Dataset, tuple_.dataset.key)

            compute_plan = None
            if tuple_.compute_plan_id:
                compute_plan = self._db.get(schemas.Type.ComputePlan, tuple_.compute_plan_id)

            # prepare model and datasamples
            data_volume = self._get_data_volume(tuple_dir, tuple_)
            predictions_volume = _mkdir(os.path.join(tuple_dir, "pred"))
            models_volume = _mkdir(os.path.join(tuple_dir, "models"))
            os.link(
                traintuple.out_model.storage_address,
                os.path.join(models_volume, traintuple.out_model.key),
            )
            volumes = {
                dataset.data_opener: _VOLUME_OPENER,
                data_volume: _VOLUME_INPUT_DATASAMPLES,
                models_volume: _VOLUME_MODELS_RO,
                predictions_volume: _VOLUME_OUTPUT_PRED,
            }
            if tuple_.compute_plan_id:
                local_volume = _mkdir(
                    os.path.join(
                        self._wdir, "compute_plans", "local", tuple_.compute_plan_id
                    )
                )
                volumes[local_volume] = _VOLUME_LOCAL

            # compute testtuple command
            model_container_address = pathlib.Path(
                os.path.join(models_volume, traintuple.out_model.key).replace(
                    models_volume, _VOLUME_MODELS_RW["bind"]
                )
            )
            command = f"predict {model_container_address}"

            container_name = f"algo-{traintuple.algo_key}"
            logs = self._spawner.spawn(
                container_name, str(algo.file), command, volumes=volumes
            )

            # Calculate the metrics
            volumes = {
                predictions_volume: _VOLUME_OUTPUT_PRED,
                dataset.data_opener: _VOLUME_OPENER,
                data_volume: _VOLUME_INPUT_DATASAMPLES,
            }
            # TODO do we add the compute plan volume ?

            command = f"--fake-data-mode {METRICS_NO_FAKE_Y}"

            container_name = DOCKER_METRICS_TAG
            logs_predict = self._spawner.spawn(
                container_name, str(objective.metrics), command=command, volumes=volumes
            )

            # save move performances
            tmp_path = os.path.join(predictions_volume, "perf.json")
            pred_dir = _mkdir(os.path.join(self._wdir, "performances", tuple_.key))
            pred_path = os.path.join(pred_dir, "performance.json")
            shutil.copy(tmp_path, pred_path)

            with open(pred_path, 'r') as f:
                tuple_.dataset.perf = json.load(f).get('all')

            # set logs and status
            tuple_.log = "\n".join(logs)
            tuple_.log += "\n".join(logs_predict)
            tuple_.status = models.Status.done

            if compute_plan:
                compute_plan.done_count += 1
                if compute_plan.done_count == compute_plan.tuple_count:
                    compute_plan.status = models.Status.done
