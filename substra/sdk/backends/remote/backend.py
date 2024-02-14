import json
import logging
import math
from copy import deepcopy
from typing import Dict
from typing import List
from typing import Union

from substra.sdk import compute_plan
from substra.sdk import exceptions
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.backends import base
from substra.sdk.backends.remote import rest_client

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60
AUTO_BATCHING = "auto_batching"
BATCH_SIZE = "batch_size"
DOWNLOAD_CHUNK_SIZE = 1024


def _find_asset_field(data, field):
    """Find data value where location is defined as `field.subfield...`."""
    for f in field.split("."):
        data = getattr(data, f)
    return data


class Remote(base.BaseBackend):
    def __init__(self, url, insecure, token, retry_timeout, backend_type):
        self._client = rest_client.Client(url, insecure, token)
        self._retry_timeout = retry_timeout or DEFAULT_RETRY_TIMEOUT
        assert backend_type == self.backend_mode

    @property
    def backend_mode(self) -> schemas.BackendType:
        """Get the backend mode: remote"""
        return schemas.BackendType.REMOTE

    def login(self, username, password):
        return self._client.login(username, password)

    def logout(self):
        return self._client.logout()

    def get(self, asset_type, key):
        """Get an asset by key."""
        asset = self._client.get(asset_type.to_server(), key)
        return models.SCHEMA_TO_MODEL[asset_type](**asset)

    def get_task_output_asset(self, compute_task_key: str, identifier: str) -> models.OutputAsset:
        outputs = self._client.list(
            schemas.Type.Task.to_server(),
            path=compute_task_key + "/output_assets",
            filters={"identifier": [identifier]},
        )

        if len(outputs) == 0:
            raise exceptions.TaskAssetNotFoundError(compute_task_key=compute_task_key, identifier=identifier)
        elif len(outputs) > 1:
            raise exceptions.TaskAssetMultipleFoundError(compute_task_key=compute_task_key, identifier=identifier)
        return models.OutputAsset(**outputs[0])

    def list_task_output_assets(self, compute_task_key: str) -> List[models.OutputAsset]:
        outputs = self._client.list(
            schemas.Type.Task.to_server(),
            path=compute_task_key + "/output_assets",
        )
        return [models.OutputAsset(**output) for output in outputs]

    def list_task_input_assets(self, compute_task_key: str) -> List[models.InputAsset]:
        inputs = self._client.list(
            schemas.Type.Task.to_server(),
            path=compute_task_key + "/input_assets",
        )
        return [models.InputAsset(**i) for i in inputs]

    def get_performances(self, key: str) -> models.Performances:
        """Get an compute plan performance by key."""

        compute_plan = self.get(schemas.Type.ComputePlan, key)
        response = self._client.list(schemas.Type.ComputePlan.to_server(), path=key + "/perf", paginated=False)
        results = response["results"]

        performances = models.Performances()

        for test_task in results:
            performances.compute_plan_key.append(compute_plan.key)
            performances.compute_plan_tag.append(compute_plan.tag)
            performances.compute_plan_status.append(compute_plan.status)
            performances.compute_plan_start_date.append(compute_plan.start_date)
            performances.compute_plan_end_date.append(compute_plan.end_date)
            performances.compute_plan_metadata.append(compute_plan.metadata)

            performances.worker.append(test_task["compute_task"]["worker"])
            performances.task_key.append(test_task["compute_task"]["key"])
            performances.task_rank.append(test_task["compute_task"]["rank"])
            try:
                round_idx = int(test_task["compute_task"]["round_idx"])
            except TypeError:
                round_idx = None
            performances.round_idx.append(round_idx)
            performances.identifier.append(test_task["identifier"])
            performances.performance.append(test_task["perf"])

        return performances

    def list(
        self,
        asset_type: schemas.Type,
        filters: Dict[str, Union[List[str], dict]] = None,
        order_by: str = None,
        ascending: bool = False,
        paginated: bool = True,
    ) -> List[models._Model]:
        """List assets of asset_type with filters.

        Args:
            cf [rest_client](substra.sdk.backends.rest_client.list)

        Returns:
            List[models._Model] : a List of assets
        """
        assets = self._client.list(
            asset_type=asset_type.to_server(),
            filters=filters,
            order_by=order_by,
            ascending=ascending,
            paginated=paginated,
        )
        return [models.SCHEMA_TO_MODEL[asset_type](**asset) for asset in assets]

    def _add(self, asset, data, files=None):
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        if files:
            kwargs = {
                "data": {
                    "json": json.dumps(data),
                },
                "files": files,
            }

        else:
            kwargs = {
                "json": data,
            }

        return self._client.add(
            asset.to_server(),
            retry_timeout=self._retry_timeout,
            **kwargs,
        )

    def _add_data_samples(self, spec, spec_options):
        """Add data sample(s)."""
        # data sample(s) creation must be handled separately as the get request is not
        # available on this ressource.
        try:
            with spec.build_request_kwargs(**spec_options) as (data, files):
                data_samples = self._add(schemas.Type.DataSample, data, files)
        except exceptions.AlreadyExists as e:
            if spec.is_many():
                # We don't know which of the keys already exists
                raise

            key = e.key[0]
            logger.warning(f"data_sample already exists: key='{key}'")
            data_samples = [{"key": key}]

        # there is currently a single route in the backend to add a single or many
        # datasamples, this route always returned a list of created data sample keys
        return [data_sample["key"] for data_sample in data_samples] if spec.is_many() else data_samples[0]["key"]

    def add(self, spec, spec_options=None):
        """Add an asset."""
        spec_options = spec_options or {}
        asset_type = spec.__class__.type_
        # Remove auto_batching and batch_size from spec_options
        auto_batching = spec_options.pop(AUTO_BATCHING, False)
        batch_size = spec_options.pop(BATCH_SIZE, None)

        if asset_type == schemas.Type.DataSample:
            # data sample corner case
            return self._add_data_samples(
                spec,
                spec_options=spec_options,
            )
        elif asset_type == schemas.Type.ComputePlan:
            cp = self._add_compute_plan(spec, spec_options)
            self._add_tasks_from_computeplan(spec, spec_options, auto_batching, batch_size)
            return cp
        elif asset_type == schemas.Type.Task:
            cp_spec = schemas.ComputePlanSpec(name=f"{spec.key}")
            self._add_compute_plan(cp_spec, spec_options)
            spec.compute_plan_key = cp_spec.key
            return self._add_tasks([spec], spec_options)[0]["key"]

        with spec.build_request_kwargs(**spec_options) as (data, files):
            response = self._add(asset_type, data, files=files)

        return response["key"]

    def _add_compute_plan(self, spec, spec_options):
        """Register compute plan info (without tasks)."""
        cp_spec = spec.model_copy()
        del cp_spec.tasks

        with spec.build_request_kwargs(**spec_options) as (data, _):
            response = self._add(schemas.Type.ComputePlan, data)
        return models.ComputePlan(**response)

    def _add_tasks_from_computeplan(self, spec, spec_options, auto_batching, batch_size):
        """Register batch(es) of tasks."""
        tasks = compute_plan.get_tasks(spec)
        if auto_batching:
            if not batch_size:
                raise ValueError(
                    "Batch size must be defined to create a compute plan \
                    with the auto-batching feature."
                )
            # Split tasks by batch
            batches = []
            for i in range(math.ceil(len(tasks) / batch_size)):
                start = i * batch_size
                end = min(len(tasks), (i + 1) * batch_size)
                batches.append(tasks[start:end])
        else:
            batches = [tasks]

        for batch in batches:
            try:
                self._add_tasks(batch, spec_options)
            except exceptions.AlreadyExists:
                logger.warning(
                    "Skipping already submitted tasks, probably because of a timeout error. "
                    "Check that the compute plan has the right number of tasks once the submission is complete."
                )
                continue

    def _add_tasks(self, batch, spec_options):
        batch_data = []
        for task_spec in batch:
            with task_spec.build_request_kwargs(**spec_options) as (task_data, _):
                batch_data.append(task_data)
        return self._client.request(
            "post",
            "task",
            path="bulk_create/",
            json={"tasks": batch_data},
        )

    def _update(self, asset, key, data, files=None):
        data = deepcopy(data)  # make a deep copy for avoiding modification by reference
        if files:
            kwargs = {
                "data": {
                    "json": json.dumps(data),
                },
                "files": files,
            }

        else:
            kwargs = {
                "json": data,
            }

        return self._client.update(
            asset.to_server(),
            key,
            retry_timeout=self._retry_timeout,
            **kwargs,
        )

    def update(self, key, spec, spec_options=None):
        spec_options = spec_options or {}
        asset_type = spec.__class__.type_
        with spec.build_request_kwargs(**spec_options) as (data, files):
            return self._update(asset_type, key, data, files=files)

    def add_compute_plan_tasks(self, spec, spec_options):
        # Remove auto_batching and batch_size from spec_options
        auto_batching = spec_options.pop(AUTO_BATCHING, False)
        batch_size = spec_options.pop(BATCH_SIZE, None)
        self._add_tasks_from_computeplan(spec, spec_options, auto_batching, batch_size)

        return self.get(
            asset_type=schemas.Type.ComputePlan,
            key=spec.key,
        )

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys) -> List[str]:
        """Returns the list of the data sample keys"""
        data = {
            "data_manager_keys": [dataset_key],
            "data_sample_keys": data_sample_keys,
        }
        self._client.request(
            "post",
            schemas.Type.DataSample.to_server(),
            path="bulk_update/",
            data=data,
        )
        return data_sample_keys

    def _download(self, url: str, destination_file: str) -> str:
        response = self._client.get_data(url, stream=True)
        with open(destination_file, "wb") as f:
            for chunk in response.iter_content(DOWNLOAD_CHUNK_SIZE):
                f.write(chunk)

        return destination_file

    def download(self, asset_type: schemas.Type, url_field_path: str, key: str, destination: str) -> str:
        data = self.get(asset_type, key)
        url = _find_asset_field(data, url_field_path)
        return self._download(url, destination)

    def download_model(self, key: str, destination_file: str) -> str:
        url = f"{self._client.base_url}/model/{key}/file/"
        return self._download(url, destination_file)

    def download_logs(self, task_key: str, destination_file: str = None) -> str:
        """Download the logs of a failed task. If destination_file is set, return the full
        destination path, otherwise, return the logs as a str.
        """
        url = f"{self._client.base_url}/task/{task_key}/logs/"

        if destination_file:
            return self._download(url, destination_file)

        return self._client.get_data(url).text

    def describe(self, asset_type, key):
        data = self.get(asset_type, key)
        url = data.description.storage_address
        r = self._client.get_data(url)
        return r.text

    def organization_info(self):
        response = self._client.get_data(f"{self._client.base_url}/info/")
        return models.OrganizationInfo(**response.json())

    def cancel_compute_plan(self, key: str) -> None:
        self._client.request(
            "post",
            schemas.Type.ComputePlan.to_server(),
            path=f"{key}/cancel",
        )
