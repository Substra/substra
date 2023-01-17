import copy
import logging
import shutil
import typing
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional

from tqdm.auto import tqdm

import substra
from substra.sdk import compute_plan as compute_plan_module
from substra.sdk import exceptions
from substra.sdk import fs
from substra.sdk import graph
from substra.sdk import models
from substra.sdk import schemas
from substra.sdk.backends import base
from substra.sdk.backends.local import compute
from substra.sdk.backends.local import dal

logger = logging.getLogger(__name__)

_MAX_LEN_KEY_METADATA = 50
_MAX_LEN_VALUE_METADATA = 100


class Local(base.BaseBackend):

    org_counter = 1

    def __init__(self, backend, backend_type, *args, **kwargs):
        self._local_worker_dir = Path.cwd() / "local-worker"
        self._local_worker_dir.mkdir(exist_ok=True)

        self._execution_mode = backend_type
        # create a store to abstract the db
        self._db = dal.DataAccess(backend, local_worker_dir=self._local_worker_dir)
        self._worker = compute.Worker(
            self._db,
            local_worker_dir=self._local_worker_dir,
            debug_spawner=self._execution_mode,
        )

        self._org_id = f"MyOrg{Local.org_counter}MSP"
        self._org_name = f"MyOrg{Local.org_counter}MSP"
        Local.org_counter += 1
        self._db.add(
            models.Organization(
                id=self._org_id,
                is_current=False,  # all orgs share the same db, catch and change this value at the "get"
                creation_date=self.__now(),
            )
        )

    def __now(self):
        """Return the current date in the iso format"""
        return datetime.now()

    @property
    def temp_directory(self):
        """Get the temporary directory where the assets are saved.
        The directory is deleted at the end of the execution."""
        return self._db.tmp_dir

    @property
    def backend_mode(self) -> schemas.BackendType:
        """Get the backend mode"""
        return self._execution_mode

    def login(self, username, password):
        self._db.login(username, password)

    def get(self, asset_type, key):
        return self._db.get(asset_type, key)

    def get_performances(self, key):

        performances = self._db.get_performances(key)

        return performances

    def list(
        self,
        asset_type: schemas.Type,
        filters: Dict[str, List[str]] = None,
        order_by: str = None,
        ascending: bool = False,
        paginated: bool = True,
    ) -> List[models._Model]:
        """List the assets

        Args:
            paginated (bool, optional): True if server response is expected to be paginated.
                Ignored for local backend (responses are never paginated)
            others: cf [dal](substra.sdk.backends.local.dal.list)

        Returns:
            List[models._Model]: List of results
        """
        results = self._db.list(type_=asset_type, filters=filters, order_by=order_by, ascending=ascending)
        if asset_type == schemas.Type.Organization:
            for i, item in enumerate(results):
                if item.id == self._org_id:
                    my_org = copy.copy(item)  # do not change the value in the db
                    my_org.is_current = True
                    results[i] = my_org
        return results

    @staticmethod
    def _check_metadata(metadata: Optional[Dict[str, str]]):
        if metadata is not None:
            if any([len(key) > _MAX_LEN_KEY_METADATA for key in metadata]):
                raise exceptions.InvalidRequest("The key in metadata cannot be more than 50 characters", 400)
            if any([len(value) > _MAX_LEN_VALUE_METADATA or len(value) == 0 for value in metadata.values()]):
                raise exceptions.InvalidRequest("Values in metadata cannot be empty or more than 100 characters", 400)
            if any("__" in key for key in metadata):
                raise exceptions.InvalidRequest(
                    '"__" cannot be used in a metadata key, please use simple underscore instead', 400
                )

    def _check_data_samples(self, spec: schemas.TaskSpec):
        """Get all the data samples from the db once and run sanity checks on them"""

        dataset_input_ref = [
            input_ref.asset_key
            for input_ref in spec.inputs
            if input_ref.identifier == schemas.StaticInputIdentifier.opener
        ]
        data_sample_keys = [
            input_ref.asset_key
            for input_ref in spec.inputs
            if input_ref.identifier == schemas.StaticInputIdentifier.datasamples
        ]

        if len(dataset_input_ref) == 1 and len(data_sample_keys) > 0:
            data_manager_key = dataset_input_ref[0]
            data_samples = self.list(schemas.Type.DataSample, filters={"key": data_sample_keys})

            if self._db.is_local(data_manager_key, schemas.Type.Dataset):
                data_manager = self._db.get(schemas.Type.Dataset, data_manager_key)
                if data_manager.owner != spec.worker:
                    raise substra.exceptions.InvalidRequest(
                        f"The task worker must be the organization that contains the data: {data_manager.owner}", 400
                    )

            # Check that we've got all the data_samples
            if len(data_samples) != len(data_sample_keys):
                raise substra.exceptions.InvalidRequest(
                    "Could not get all the data_samples in the database with the given data_sample_keys", 400
                )

            self._check_same_data_manager(data_manager_key, data_samples)

    def _check_same_data_manager(self, data_manager_key, data_samples):
        """Check that all data samples are linked to this data manager"""
        # If the dataset is remote: the backend does not return the datasets
        # linked to each sample, so no check (already done in the backend).
        if self._db.is_local(data_manager_key, schemas.Type.Dataset):
            same_data_manager = all(
                [data_manager_key in data_sample.data_manager_keys for data_sample in (data_samples or list())]
            )
            if not same_data_manager:
                raise substra.exceptions.InvalidRequest("A data_sample does not belong to the same dataManager", 400)

    def __compute_permissions(self, permissions):
        """Compute the permissions

        If the permissions are private, the active organization is
        in the authorized ids.
        """
        owner = self._org_id
        if permissions.public:
            permissions.authorized_ids = list()
        elif not permissions.public and owner not in permissions.authorized_ids:
            permissions.authorized_ids.append(owner)
        return permissions

    def __add_compute_plan(
        self,
        task_count,
    ):
        key = schemas._Spec.compute_key()
        compute_plan = models.ComputePlan(
            key=key,
            creation_date=self.__now(),
            start_date=self.__now(),
            status=models.ComputePlanStatus.waiting,
            tag="",
            name=key,
            task_count=task_count,
            todo_count=task_count,
            metadata=dict(),
            owner="local",
            delete_intermediary_models=False,
        )

        return self._db.add(compute_plan)

    def __create_compute_plan_from_tuple(self, spec, in_tuples):
        # compute plan and rank
        if spec.compute_plan_key is not None:
            compute_plan = self._db.get(schemas.Type.ComputePlan, spec.compute_plan_key)
            compute_plan_key = compute_plan.key
            if spec.rank is not None:
                # Use the rank given by the user
                rank = spec.rank
            else:
                if len(in_tuples) == 0:
                    rank = 0
                else:
                    rank = 1 + max(
                        [in_tuple.rank for in_tuple in in_tuples if in_tuple.compute_plan_key == compute_plan_key]
                    )

            # Add to the compute plan
            compute_plan.task_count += 1
            compute_plan.todo_count += 1
            compute_plan.status = models.Status.waiting

        elif not spec.compute_plan_key and (spec.rank == 0 or spec.rank is None):
            # Create a compute plan
            compute_plan = self.__add_compute_plan(task_count=1)
            rank = 0
            compute_plan_key = compute_plan.key
        else:
            raise substra.sdk.exceptions.InvalidRequest("invalid inputs, a new ComputePlan should have a rank 0", 400)

        return compute_plan_key, rank

    def __execute_compute_plan(self, spec, compute_plan, visited, tuples, spec_options):
        with tqdm(
            total=len(visited),
            desc="Compute plan progress",
        ) as progress_bar:

            for id_, _ in sorted(visited.items(), key=lambda item: item[1]):

                tuple_spec = tuples.get(id_)
                if not tuple_spec:
                    continue

                self.add(
                    key=tuple_spec.key,
                    spec=tuple_spec,
                    spec_options=spec_options,
                )

                progress_bar.update()

        return compute_plan

    def _add_algo(self, key, spec, spec_options=None):
        self._check_metadata(spec.metadata)
        permissions = self.__compute_permissions(spec.permissions)
        algo_file_path = self._db.save_file(spec.file, key)
        algo_description_path = self._db.save_file(spec.description, key)

        algo = models.Algo(
            key=key,
            creation_date=self.__now(),
            name=spec.name,
            owner=self._org_id,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            algorithm={"checksum": fs.hash_file(algo_file_path), "storage_address": algo_file_path},
            description={"checksum": fs.hash_file(algo_description_path), "storage_address": algo_description_path},
            metadata=spec.metadata if spec.metadata else dict(),
            inputs=spec.inputs or list(),
            outputs=spec.outputs or list(),
        )
        return self._db.add(algo)

    def _add_dataset(self, key, spec, spec_options=None):

        self._check_metadata(spec.metadata)

        permissions = self.__compute_permissions(spec.permissions)
        logs_permission = self.__compute_permissions(spec.logs_permission)

        dataset_file_path = self._db.save_file(spec.data_opener, key)
        dataset_description_path = self._db.save_file(spec.description, key)
        asset = models.Dataset(
            key=key,
            creation_date=self.__now(),
            owner=self._org_id,
            name=spec.name,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            type=spec.type,
            data_sample_keys=list(),
            opener={"checksum": fs.hash_file(dataset_file_path), "storage_address": dataset_file_path},
            description={
                "checksum": fs.hash_file(dataset_description_path),
                "storage_address": dataset_description_path,
            },
            metadata=spec.metadata if spec.metadata else dict(),
            logs_permission=logs_permission.dict(),
        )
        return self._db.add(asset)

    def _add_data_sample(self, key, spec, spec_options=None):
        if len(spec.data_manager_keys) == 0:
            raise exceptions.InvalidRequest("Please add at least one data manager for the data sample", 400)
        datasets = [self._db.get(schemas.Type.Dataset, dataset_key) for dataset_key in spec.data_manager_keys]

        data_sample = models.DataSample(
            key=key,
            creation_date=self.__now(),
            owner=self._org_id,
            path=spec.path,
            data_manager_keys=spec.data_manager_keys,
        )
        data_sample = self._db.add(data_sample)

        # update dataset(s) accordingly
        for dataset in datasets:
            samples_list = dataset.data_sample_keys
            if data_sample.key not in samples_list:
                samples_list.append(data_sample.key)

        return data_sample

    def _add_data_samples(self, spec, spec_options=None):
        data_samples = list()
        for path in spec.paths:
            data_sample_spec = schemas.DataSampleSpec(
                path=path,
                data_manager_keys=spec.data_manager_keys,
            )
            key = data_sample_spec.compute_key()
            data_sample = self._add_data_sample(
                key,
                data_sample_spec,
                spec_options,
            )
            data_samples.append(data_sample)
        return data_samples

    def _add_compute_plan(self, spec: schemas.ComputePlanSpec, spec_options: dict = None):
        self._check_metadata(spec.metadata)
        # Get all the tuples and their dependencies
        tuple_graph, tuples = compute_plan_module.get_dependency_graph(spec)

        # Define the rank of each task
        visited = graph.compute_ranks(node_graph=tuple_graph)

        compute_plan = models.ComputePlan(
            key=spec.key,
            creation_date=self.__now(),
            start_date=self.__now(),
            tag=spec.tag or "",
            name=spec.name,
            status=models.ComputePlanStatus.empty,
            metadata=spec.metadata or dict(),
            task_count=0,
            waiting_count=0,
            todo_count=0,
            doing_count=0,
            canceled_count=0,
            failed_count=0,
            done_count=0,
            owner=self._org_id,
        )
        compute_plan = self._db.add(compute_plan)

        # go through the tuples sorted by rank
        compute_plan = self.__execute_compute_plan(spec, compute_plan, visited, tuples, spec_options)
        return compute_plan

    def _add_task(self, key, spec, spec_options=None):
        self._check_metadata(spec.metadata)
        self._check_data_samples(spec)
        algo = self._db.get(schemas.Type.Algo, spec.algo_key)

        _warn_on_transient_outputs(spec.outputs)

        in_task_keys = list(
            {inputref.parent_task_key for inputref in (spec.inputs or list()) if inputref.parent_task_key}
        )
        in_tasks = [self._db.get(schemas.Type.Task, in_task_key) for in_task_key in in_task_keys]
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec=spec, in_tuples=in_tasks)

        task = models.Task(
            key=key,
            creation_date=self.__now(),
            algo=algo,
            owner=self._org_id,
            worker=spec.worker,
            compute_plan_key=compute_plan_key,
            rank=rank,
            inputs=spec.inputs or [],
            outputs=_output_from_spec(spec.outputs),
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata if spec.metadata else dict(),
        )

        task = self._db.add(task)
        self._worker.schedule_task(task)
        return task

    def _check_inputs_outputs(self, spec, algo_key):
        algo = self._db.get(schemas.Type.Algo, algo_key)
        spec_inputs = spec.inputs or list()
        spec_outputs = spec.outputs or dict()

        error_msg = ""
        for algo_input in algo.inputs:
            spec_values = [x for x in spec_inputs if x.identifier == algo_input.identifier]
            if len(spec_values) == 0 and not algo_input.optional:
                error_msg += f"  - The input {algo_input.identifier} is not optional according to the algo.\n"
            if len(spec_values) > 1 and not algo_input.multiple:
                error_msg += f"  - The input {algo_input.identifier} is not multiple according to the algo.\n"

        if not set([x.identifier for x in spec_inputs]).issubset(set([x.identifier for x in algo.inputs])):
            error_msg += "  - There are keys in the spec inputs that have not been declared in the algo inputs.\n"

        spec_output_keys = set([x for x in spec_outputs])
        algo_output_keys = set([x.identifier for x in algo.outputs])
        if not spec_output_keys == algo_output_keys:
            error_msg += (
                "  - The identifiers in the spec outputs and the algo outputs must match:"
                f"{spec_output_keys.symmetric_difference(algo_output_keys)}.\n"
            )

        for output_performance in (x for x in algo.outputs if x.kind == schemas.AssetKind.performance):
            if not spec_outputs[output_performance.identifier].permissions.public:
                error_msg += '  - invalid task output "performance": a PERFORMANCE output should be public.'
                break

        if len(error_msg) > 0:
            raise exceptions.InvalidRequest(f"There are errors in the inputs / outputs fields:\n{error_msg}", "OE0101")

    def add(self, spec, spec_options=None, key=None):

        algo_key = getattr(spec, "algo_key", None)
        if algo_key is not None:
            self._check_inputs_outputs(spec=spec, algo_key=algo_key)

        # find dynamically the method to call to create the asset
        method_name = f"_add_{spec.__class__.type_.value}"
        if spec.is_many():
            method_name += "s"
        add_asset = getattr(self, method_name)
        if spec.is_many():
            assets = add_asset(spec, spec_options)
            return [asset.key for asset in assets]
        else:
            if spec.__class__.type_ == schemas.Type.ComputePlan:
                compute_plan = add_asset(spec, spec_options)
                return compute_plan
            else:
                key = key or spec.compute_key()
                add_asset(key, spec, spec_options)
                return key

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys) -> List[str]:
        dataset = self._db.get(schemas.Type.Dataset, dataset_key)
        data_samples = list()
        for key in data_sample_keys:
            data_sample = self._db.get(schemas.Type.DataSample, key)
            if dataset_key not in data_sample.data_manager_keys:
                data_sample.data_manager_keys.append(dataset_key)
                dataset.data_sample_keys.append(key)
            else:
                logger.warning(f"Data sample already in dataset: {key}")
            data_samples.append(data_sample)
        return data_sample_keys

    def download(self, asset_type, url_field_path, key, destination_file):
        if self._db.is_local(key, asset_type):
            asset = self._db.get(type_=asset_type, key=key)
            # Get the field containing the path to the file.
            file_path = asset
            for field in url_field_path.split("."):
                file_path = getattr(file_path, field, None)
            # Copy the file to the destination file
            shutil.copyfile(file_path, destination_file)
        else:
            self._db.remote_download(asset_type, url_field_path, key, destination_file)

        return destination_file

    def download_model(self, key, destination_file):
        if self._db.is_local(key, schemas.Type.Model):
            asset = self._db.get(type_=schemas.Type.Model, key=key)
            shutil.copyfile(asset.address.storage_address, destination_file)
        else:
            self._db.remote_download_model(key, destination_file)

        return destination_file

    def download_logs(self, tuple_key: str, destination_file: str = None) -> NoReturn:
        raise NotImplementedError("Logs of tuples ran in local mode are not accessible")

    def describe(self, asset_type, key):
        if self._db.is_local(key, schemas.Type.Dataset):
            asset = self._db.get(type_=asset_type, key=key)
            if not hasattr(asset, "description") or not asset.description:
                raise ValueError("This element does not have a description.")
            with open(asset.description.storage_address, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return self._db.get_remote_description(asset_type, key)

    def organization_info(self):
        return models.OrganizationInfo(
            host="http://fakeurl.fake",
            organization_id=self._org_id,
            organization_name=self._org_name,
            config=models.OrganizationInfoConfig(
                model_export_enabled=True,
            ),
            channel="channel1",
            version=substra.__version__,
            orchestrator_version="fake",
        )

    def cancel_compute_plan(self, key):
        # Execution is synchronous in the local backend so this
        # function does not make sense.
        raise NotImplementedError

    def update(self, key, spec, spec_options=None):
        asset_type = spec.__class__.type_
        asset = self.get(asset_type, key)
        data = asset.dict()
        data.update(spec.dict())
        updated_asset = models.SCHEMA_TO_MODEL[asset_type](**data)
        self._db.update(updated_asset)
        return

    def add_compute_plan_tuples(self, spec: schemas.UpdateComputePlanTuplesSpec, spec_options: dict = None):
        key = spec.key
        compute_plan = self._db.get(schemas.Type.ComputePlan, key)
        # Get all the new tuples and their dependencies
        tuple_graph, tuples = compute_plan_module.get_dependency_graph(spec)

        # Get the rank of all the tuples already in the compute plan
        filters = {"compute_plan_key": [key]}
        cp_tasks = self.list(
            asset_type=schemas.Type.Task,
            filters=filters,
        )
        visited = dict()
        for task in cp_tasks:
            visited[task.key] = task.rank

        # Update the tuple graph with the tuples already in the CP
        tuple_graph.update({k: list() for k in visited})
        visited = graph.compute_ranks(node_graph=tuple_graph, ranks=visited)

        compute_plan = self.__execute_compute_plan(spec, compute_plan, visited, tuples, spec_options)
        return compute_plan


def _output_from_spec(outputs: Dict[str, schemas.ComputeTaskOutputSpec]) -> Dict[str, models.ComputeTaskOutput]:
    """Convert a list of schemas.ComputeTaskOuput to a list of models.ComputeTaskOutput"""
    return {
        identifier: models.ComputeTaskOutput(
            permissions=models.Permissions(process=output.permissions), transient=output.is_transient, value=None
        )
        # default isNone (= outputs are not computed yet)
        for identifier, output in outputs.items()
    }


def _warn_on_transient_outputs(outputs: typing.Dict[str, schemas.ComputeTaskOutputSpec]):
    for _, output in outputs.items():
        if output.is_transient:
            warnings.warn("`transient=True` is ignored in local mode")
