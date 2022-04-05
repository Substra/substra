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
import logging
import os
import shutil
import warnings
from datetime import datetime
from distutils import util
from pathlib import Path
from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Tuple

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
from substra.sdk.config import BackendType

logger = logging.getLogger(__name__)

_BACKEND_ID = "local-backend"
_MAX_LEN_KEY_METADATA = 50
_MAX_LEN_VALUE_METADATA = 100
DEBUG_OWNER = "debug_owner"


class Local(base.BaseBackend):
    def __init__(self, backend, *args, **kwargs):
        self._local_worker_dir = Path.cwd() / "local-worker"
        self._local_worker_dir.mkdir(exist_ok=True)

        self._support_chainkeys = bool(util.strtobool(os.getenv("CHAINKEYS_ENABLED", "False")))
        self._chainkey_dir = self._local_worker_dir / "chainkeys"
        if self._support_chainkeys:
            logger.info(f"Chainkeys support is on, the directory is {self._chainkey_dir}")

        self._debug_spawner = BackendType(os.getenv("DEBUG_SPAWNER", BackendType.LOCAL_DOCKER))
        if self._debug_spawner == BackendType.LOCAL_SUBPROCESS:
            logger.info(
                "Environment variable DEBUG_SPAWNER is set to subprocess: "
                "running Substra tasks with Python subprocess"
            )

        # create a store to abstract the db
        self._db = dal.DataAccess(backend, local_worker_dir=self._local_worker_dir)
        self._worker = compute.Worker(
            self._db,
            local_worker_dir=self._local_worker_dir,
            support_chainkeys=self._support_chainkeys,
            debug_spawner=self._debug_spawner,
            chainkey_dir=self._chainkey_dir,
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
    def backend_mode(self) -> BackendType:
        """Get the backend mode"""
        return self._debug_spawner

    def login(self, username, password):
        self._db.login(username, password)

    def get(self, asset_type, key):
        asset = self._db.get(asset_type, key)

        # extra data for tasks

        if asset_type == schemas.Type.Traintuple:
            asset.train.data_manager = self._db.get(schemas.Type.Dataset, asset.train.data_manager_key)
        if asset_type == schemas.Type.CompositeTraintuple:
            asset.composite.data_manager = self._db.get(schemas.Type.Dataset, asset.composite.data_manager_key)
        if asset_type == schemas.Type.Testtuple:
            asset.test.data_manager = self._db.get(schemas.Type.Dataset, asset.test.data_manager_key)
            asset.test.metrics = [self._db.get(schemas.Type.Metric, k) for k in asset.test.metric_keys]
        if asset_type in [
            schemas.Type.Traintuple,
            schemas.Type.CompositeTraintuple,
            schemas.Type.Aggregatetuple,
            schemas.Type.Testtuple,
        ]:
            asset.parent_tasks = [self._get_parent_task(key) for key in asset.parent_task_keys]

        return asset

    def _get_parent_task(self, key):
        for tuple_type in [
            schemas.Type.Traintuple,
            schemas.Type.CompositeTraintuple,
            schemas.Type.Aggregatetuple,
        ]:
            try:
                return self._db.get(tuple_type, key)
            except exceptions.NotFound:
                pass

        raise exceptions.NotFound(f"Wrong pk {key}", 404)

    def _filter_match_split(
        self, db_assets: List[models._Model], match_filters: List[str]
    ) -> Tuple[List[models._Model], List[models._Model]]:
        """Return assets matching all filters (AND group), and the remaining ones"""
        matching_assets = []
        remaining_assets = []
        for asset in db_assets:
            # the filters use the 'response' (ie camel case) format
            if all([str(getattr(asset, key)) == value for key, value in match_filters.items()]):
                matching_assets.append(asset)
            else:
                remaining_assets.append(asset)
        return matching_assets, remaining_assets

    def _filter_assets(self, db_assets: List[models._Model], filters: List[str]) -> List[models._Model]:
        """Filter the assets
        C.f. the list function for doc
        """
        if filters is None or len(filters) == 0:
            return db_assets

        remaining_assets = db_assets
        parsed_filters = dict()
        result = list()

        for filter_ in filters:
            if filter_ == "OR":
                if not parsed_filters:
                    raise ValueError("Couldn't parse filters before OR statement")
                # filter the remaining (non-matched) assets with the previous "AND group" of parsed filters
                matching_assets, remaining_assets = self._filter_match_split(remaining_assets, parsed_filters)
                result.extend(matching_assets)
                # reset the filters
                parsed_filters = dict()
            elif filter_ == "AND":
                if not parsed_filters:
                    raise ValueError("Couldn't parse filter before AND statement")
                # continue parsing filters
            else:
                splitted = filter_.split(":")
                if len(splitted) < 3:
                    raise ValueError(
                        f"Wrong filter format, found {filter_}, must be 'asset_type:field_name:field_value'/'OR'/'AND'"
                    )
                field_name = splitted[1]
                field_value = "".join(splitted[2:])
                if field_name in parsed_filters:
                    raise ValueError(f"filter '{filter_}': can't apply filter on the same field twice in a 'AND group'")
                parsed_filters[field_name] = field_value

        assert parsed_filters, "Can't parse filters"
        # filter the remaining (non-matched) assets with the last (or only) "AND group" of parsed filters
        matching_assets, _ = self._filter_match_split(remaining_assets, parsed_filters)
        result.extend(matching_assets)
        return result

    def list(self, asset_type: schemas.Type, filters: List[str] = None, paginated: bool = True) -> List[models._Model]:
        """List the assets

        This is a simplified version of the backend 'list' function

        The format of the filters is 'asset_type:field_name:field_value'
        the function returns the assets whose fields equal those values.
        It also support 'AND' and 'OR' statement as a list item between 2 filters.
        AND filter are prioritized : filter AND filter OR filter === (filter AND filter) OR filter
        Example of filters:
        ["traintuple:compute_plan_key:abc"]
        ["testtuple:compute_plan_key:abc", "AND", "testtuple:data_manager_key:42", "OR",
         "testtuple:compute_plan_key:abc"]


        Args:
            asset_type (schemas.Type): Type of asset to return
            filters (str, optional): Filter the list of results. Defaults to None.
            paginated (bool): True if server response is expected to be paginated.
                Ignored for local backend (responses are never paginated)

        Returns:
            List[models._Model]: List of results
        """
        db_assets = self._db.list(asset_type, filters)

        # Some filters in self._db.list() (substra/sdk/backends/local/dal.list) are not working, so we have to apply the
        # filters after.
        # TODO: once remote filters (substra/sdk/backends/remote/backend.list) are fixed, move the _filter_assets
        # function to substra/sdk/backends/local/db.InMemoryDb.list
        result = self._filter_assets(db_assets, filters)

        return result

    @staticmethod
    def _check_metadata(metadata: Optional[Dict[str, str]]):
        if metadata is not None:
            if any([len(key) > _MAX_LEN_KEY_METADATA for key in metadata]):
                raise exceptions.InvalidRequest("The key in metadata cannot be more than 50 characters", 400)
            if any([len(value) > _MAX_LEN_VALUE_METADATA or len(value) == 0 for value in metadata.values()]):
                raise exceptions.InvalidRequest("Values in metadata cannot be empty or more than 100 characters", 400)

        # In debug mode, the user can define the owner of the data
        if metadata is not None and DEBUG_OWNER in metadata:
            owner = metadata[DEBUG_OWNER]
        else:
            owner = _BACKEND_ID
        return owner

    @staticmethod
    def __compute_permissions(permissions, owner=_BACKEND_ID):
        """Compute the permissions

        If the permissions are private, the active node is
        in the authorized ids.
        """
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
            task_count=task_count,
            todo_count=task_count,
            metadata=dict(),
            owner="local",
            delete_intermediary_models=False,
        )
        return self._db.add(compute_plan)

    def __create_compute_plan_from_tuple(self, spec, key, in_tuples):
        # compute plan and rank
        if not spec.compute_plan_key and spec.rank == 0:
            #  Create a compute plan
            compute_plan = self.__add_compute_plan(task_count=1)
            rank = 0
            compute_plan_key = compute_plan.key
        elif not spec.compute_plan_key and spec.rank is not None:
            raise substra.sdk.exceptions.InvalidRequest("invalid inputs, a new ComputePlan should have a rank 0", 400)
        elif spec.compute_plan_key:
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

        else:
            compute_plan_key = ""
            rank = 0

        return compute_plan_key, rank

    def __execute_compute_plan(
        self, spec, compute_plan, visited, traintuples, aggregatetuples, compositetuples, spec_options
    ):
        testtuples = dict()
        if spec.testtuples:
            for testtuple in spec.testtuples:
                testtuples.setdefault(testtuple.traintuple_id, []).append(testtuple)

        with tqdm(
            total=len(visited) + len(testtuples),
            desc="Compute plan progress",
        ) as progress_bar:

            for id_, rank in sorted(visited.items(), key=lambda item: item[1]):

                if id_ in traintuples:
                    traintuple = traintuples[id_]
                    traintuple_spec = schemas.TraintupleSpec.from_compute_plan(
                        compute_plan_key=compute_plan.key, rank=rank, spec=traintuple
                    )
                    self._add_traintuple(key=id_, spec=traintuple_spec, spec_options=spec_options)

                elif id_ in aggregatetuples:
                    aggregatetuple = aggregatetuples[id_]
                    aggregatetuple_spec = schemas.AggregatetupleSpec.from_compute_plan(
                        compute_plan_key=compute_plan.key, rank=rank, spec=aggregatetuple
                    )
                    self._add_aggregatetuple(
                        key=id_,
                        spec=aggregatetuple_spec,
                        spec_options=spec_options,
                    )

                elif id_ in compositetuples:
                    compositetuple = compositetuples[id_]
                    compositetuple_spec = schemas.CompositeTraintupleSpec.from_compute_plan(
                        compute_plan_key=compute_plan.key, rank=rank, spec=compositetuple
                    )
                    self._add_composite_traintuple(
                        key=id_,
                        spec=compositetuple_spec,
                        spec_options=spec_options,
                    )
                progress_bar.update()

                # Execute the testtuple right after its train task
                if id_ in testtuples:
                    for testtuple in testtuples[id_]:
                        testtuple_spec = schemas.TesttupleSpec.from_compute_plan(spec=testtuple)
                        self.add(testtuple_spec, spec_options)
                        progress_bar.update()

        compute_plan.end_date = datetime.now()
        compute_plan.estimated_end_date = compute_plan.end_date
        compute_plan.duration = int((compute_plan.end_date - compute_plan.start_date).total_seconds())

        return compute_plan

    def __check_data_samples(self, data_manager_key: str, data_sample_keys: List[str], allow_test_only: bool):
        """Get all the data samples from the db once and run sanity checks on them"""

        filters = " OR ".join([f"datasample:key:{data_sample_key}" for data_sample_key in data_sample_keys]).split(" ")
        data_samples = self.list(schemas.Type.DataSample, filters=filters)

        # Check that we've got all the data_samples
        if len(data_samples) != len(data_sample_keys):
            raise substra.exceptions.InvalidRequest(
                "Could not get all the data_samples in the database with the given data_sample_keys", 400
            )

        self.__check_same_data_manager(data_manager_key, data_samples)
        if not allow_test_only:
            self.__check_not_test_data(data_samples)

    def __check_same_data_manager(self, data_manager_key, data_samples):
        """Check that all data samples are linked to this data manager"""
        # If the dataset is remote: the backend does not return the datasets
        # linked to each sample, so no check (already done in the backend).
        if self._db.is_local(data_manager_key, schemas.Type.Dataset):
            same_data_manager = all(
                [data_manager_key in data_sample.data_manager_keys for data_sample in (data_samples or list())]
            )
            if not same_data_manager:
                raise substra.exceptions.InvalidRequest("A data_sample does not belong to the same dataManager", 400)

    def __check_not_test_data(self, data_samples):
        """Check that we do not use test data samples for train tuples"""
        for data_sample in data_samples:
            if data_sample.test_only:
                raise substra.exceptions.InvalidRequest("Cannot create train task with test data", 400)

    def __add_algo(self, key, spec, owner, spec_options=None):

        permissions = self.__compute_permissions(spec.permissions, owner)
        algo_file_path = self._db.save_file(spec.file, key)
        algo_description_path = self._db.save_file(spec.description, key)
        algo = models.Algo(
            key=key,
            creation_date=self.__now(),
            name=spec.name,
            owner=owner,
            category=spec.category,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            algorithm={"checksum": fs.hash_file(algo_file_path), "storage_address": algo_file_path},
            description={"checksum": fs.hash_file(algo_description_path), "storage_address": algo_description_path},
            metadata=spec.metadata if spec.metadata else dict(),
        )
        return self._db.add(algo)

    def _add_algo(self, key, spec, spec_options=None):
        owner = self._check_metadata(spec.metadata)
        return self.__add_algo(key, spec, owner, spec_options=spec_options)

    def _add_dataset(self, key, spec, spec_options=None):

        owner = self._check_metadata(spec.metadata)

        permissions = self.__compute_permissions(spec.permissions, owner)
        logs_permission = self.__compute_permissions(spec.logs_permission, owner)

        dataset_file_path = self._db.save_file(spec.data_opener, key)
        dataset_description_path = self._db.save_file(spec.description, key)
        asset = models.Dataset(
            key=key,
            creation_date=self.__now(),
            owner=owner,
            name=spec.name,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            type=spec.type,
            train_data_sample_keys=list(),
            test_data_sample_keys=list(),
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
            owner=_BACKEND_ID,
            path=spec.path,
            data_manager_keys=spec.data_manager_keys,
            test_only=spec.test_only,
        )
        data_sample = self._db.add(data_sample)

        # update dataset(s) accordingly
        for dataset in datasets:
            if spec.test_only:
                samples_list = dataset.test_data_sample_keys
            else:
                samples_list = dataset.train_data_sample_keys
            if data_sample.key not in samples_list:
                samples_list.append(data_sample.key)

        return data_sample

    def _add_data_samples(self, spec, spec_options=None):
        data_samples = list()
        for path in spec.paths:
            data_sample_spec = schemas.DataSampleSpec(
                path=path,
                data_manager_keys=spec.data_manager_keys,
                test_only=spec.test_only,
            )
            key = data_sample_spec.compute_key()
            data_sample = self._add_data_sample(
                key,
                data_sample_spec,
                spec_options,
            )
            data_samples.append(data_sample)
        return data_samples

    def _add_metric(self, key, spec, spec_options):

        owner = self._check_metadata(spec.metadata)

        permissions = self.__compute_permissions(spec.permissions, owner)

        # Copy files to the local dir
        metric_file_path = self._db.save_file(spec.file, key)
        metric_description_path = self._db.save_file(spec.description, key)

        # create metric model instance
        metric = models.Metric(
            key=key,
            creation_date=self.__now(),
            name=spec.name,
            owner=owner,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            description={"checksum": fs.hash_file(metric_description_path), "storage_address": metric_description_path},
            address={"checksum": fs.hash_file(metric_file_path), "storage_address": metric_file_path},
            metadata=spec.metadata if spec.metadata else dict(),
        )

        # add metric to storage and update optionnally the associated dataset
        metric = self._db.add(metric)

        return metric

    def _add_compute_plan(self, key: str, spec: schemas.ComputePlanSpec, spec_options: dict = None):
        if spec.clean_models:
            warnings.warn("'clean_models=True' is ignored on the local backend.")
        self._check_metadata(spec.metadata)
        # Get all the tuples and their dependencies
        (tuple_graph, traintuples, aggregatetuples, compositetuples) = compute_plan_module.get_dependency_graph(spec)

        # If chainkey is supported make sure it exists, else set support to False
        if self._support_chainkeys and not (self._chainkey_dir / "node_name_id.json").is_file():
            logger.warning(f"No chainkeys found in {self._chainkey_dir}.")

        # Define the rank of each traintuple, aggregate tuple and composite tuple
        visited = graph.compute_ranks(node_graph=tuple_graph)

        compute_plan = models.ComputePlan(
            key=key,
            creation_date=self.__now(),
            start_date=self.__now(),
            tag=spec.tag or "",
            status=models.ComputePlanStatus.waiting,
            metadata=spec.metadata or dict(),
            task_count=0,
            waiting_count=0,
            todo_count=0,
            doing_count=0,
            canceled_count=0,
            failed_count=0,
            done_count=0,
            owner="local",
            delete_intermediary_models=spec.clean_models if spec.clean_models is not None else False,
        )
        compute_plan = self._db.add(compute_plan)

        # go through the tuples sorted by rank
        compute_plan = self.__execute_compute_plan(
            spec, compute_plan, visited, traintuples, aggregatetuples, compositetuples, spec_options
        )
        return compute_plan

    # TODO: '_add_traintuple' is too complex, consider refactoring
    def _add_traintuple(self, key, spec, spec_options=None):  # noqa: C901
        # validation
        owner = self._check_metadata(spec.metadata)

        algo = self._db.get(schemas.Type.Algo, spec.algo_key)
        assert algo.category == schemas.AlgoCategory.simple

        dataset = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        in_tuples = []
        if spec.in_models_keys is not None:
            for in_tuple_key in spec.in_models_keys:
                in_tuple = None
                for in_tuple_type in [schemas.Type.Traintuple, schemas.Type.Aggregatetuple]:
                    try:
                        in_tuple = self._db.get(in_tuple_type, in_tuple_key)
                        break
                    except exceptions.NotFound:
                        pass

                if in_tuple is None:
                    raise exceptions.NotFound(f"Wrong pk {key}", 404)
                else:
                    in_tuples.append(in_tuple)

        self.__check_data_samples(
            data_manager_key=spec.data_manager_key, data_sample_keys=spec.train_data_sample_keys, allow_test_only=False
        )

        # permissions
        with_permissions = [algo, dataset] + in_tuples

        public = True
        authorized_ids = None
        for element in with_permissions:
            permissions = None
            if hasattr(element, "permissions"):
                permissions = element.permissions
            elif hasattr(element, "train"):
                permissions = element.train.model_permissions
            else:
                permissions = element.aggregate.model_permissions
            public = public and permissions.process.public
            if not permissions.process.public:
                if authorized_ids is None:
                    authorized_ids = set(permissions.process.authorized_ids)
                else:
                    authorized_ids = set.intersection(authorized_ids, set(permissions.process.authorized_ids))
        if public or authorized_ids is None:
            authorized_ids = list()
        else:
            authorized_ids = list(authorized_ids)

        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec=spec, key=key, in_tuples=in_tuples)

        # create model
        traintuple = models.Traintuple(
            train={
                "data_manager_key": spec.data_manager_key,
                "data_sample_keys": spec.train_data_sample_keys,
                "model_permissions": {
                    "process": {"public": public, "authorized_ids": authorized_ids},
                },
                "models": None,
            },
            key=key,
            creation_date=self.__now(),
            category=models.TaskCategory.train,
            algo=algo,
            owner=owner,
            worker=dataset.owner,
            compute_plan_key=compute_plan_key,
            rank=rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata if spec.metadata else dict(),
            parent_task_keys=spec.in_models_keys or list(),
        )

        traintuple = self._db.add(traintuple)
        self._worker.schedule_traintuple(traintuple)
        return traintuple

    def _add_testtuple(self, key, spec, spec_options=None):

        # validation
        owner = self._check_metadata(spec.metadata)

        traintuple = self._get_parent_task(spec.traintuple_key)

        if traintuple.status in [models.Status.failed, models.Status.canceled]:
            raise substra.exceptions.InvalidRequest(
                f"could not register this testtuple, \
                the traintuple {traintuple.key} has a status {traintuple.status}",
                400,
            )

        dataset = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        self.__check_data_samples(
            data_manager_key=spec.data_manager_key, data_sample_keys=spec.test_data_sample_keys, allow_test_only=True
        )

        assert len(spec.test_data_sample_keys) > 0
        dataset_key = spec.data_manager_key
        test_data_sample_keys = spec.test_data_sample_keys
        worker = dataset.owner

        if traintuple.compute_plan_key:
            compute_plan = self._db.get(schemas.Type.ComputePlan, traintuple.compute_plan_key)
            compute_plan.task_count += 1
            compute_plan.todo_count += 1
            compute_plan.status = models.Status.waiting

        testtuple = models.Testtuple(
            test=models._Test(
                data_manager_key=dataset_key,
                data_sample_keys=test_data_sample_keys,
                metric_keys=spec.metric_keys,
                perfs={},
            ),
            key=key,
            creation_date=self.__now(),
            category=models.TaskCategory.test,
            algo=traintuple.algo,
            owner=owner,
            worker=worker,
            compute_plan_key=traintuple.compute_plan_key,
            rank=traintuple.rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata if spec.metadata else dict(),
            parent_task_keys=[spec.traintuple_key],
        )
        testtuple = self._db.add(testtuple)
        self._worker.schedule_testtuple(testtuple)
        return testtuple

    def _add_composite_traintuple(self, key: str, spec: schemas.CompositeTraintupleSpec, spec_options=None):
        # validation
        owner = self._check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.Algo, spec.algo_key)
        assert algo.category == schemas.AlgoCategory.composite
        dataset = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        self.__check_data_samples(
            data_manager_key=spec.data_manager_key, data_sample_keys=spec.train_data_sample_keys, allow_test_only=False
        )
        in_tuples = list()
        if spec.in_head_model_key:
            in_head_tuple = self._db.get(schemas.Type.CompositeTraintuple, spec.in_head_model_key)
            in_tuples.append(in_head_tuple)

        if spec.in_trunk_model_key:
            try:
                # in trunk model is a composite traintuple out trunk model
                in_trunk_tuple = self._db.get(schemas.Type.CompositeTraintuple, spec.in_trunk_model_key)
            except exceptions.NotFound:
                # in trunk model is an aggregate tuple out model
                in_trunk_tuple = self._db.get(schemas.Type.Aggregatetuple, spec.in_trunk_model_key)
            in_tuples.append(in_trunk_tuple)

        # Compute plan
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

        # permissions
        process_trunk_model_permissions = schemas.Permissions(
            public=False, authorized_ids=spec.out_trunk_model_permissions.authorized_ids
        )
        trunk_model_permissions = {"process": self.__compute_permissions(process_trunk_model_permissions)}
        if spec.in_head_model_key:
            head_model_permissions = in_head_tuple.composite.head_permissions
        else:
            head_model_permissions = {"process": {"public": False, "authorized_ids": [owner]}}

        parent_task_keys: List[str] = list()
        if spec.in_head_model_key is not None:
            parent_task_keys.append(spec.in_head_model_key)
        if spec.in_trunk_model_key is not None:
            parent_task_keys.append(spec.in_trunk_model_key)

        composite_traintuple = models.CompositeTraintuple(
            composite=models._Composite(
                data_manager_key=spec.data_manager_key,
                data_sample_keys=spec.train_data_sample_keys,
                head_permissions=head_model_permissions,
                trunk_permissions=trunk_model_permissions,
                models=list(),
            ),
            key=key,
            creation_date=self.__now(),
            category=models.TaskCategory.composite,
            algo=algo,
            owner=owner,
            worker=dataset.owner,
            compute_plan_key=compute_plan_key,
            rank=rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata if spec.metadata else dict(),
            parent_task_keys=parent_task_keys,
        )
        composite_traintuple = self._db.add(composite_traintuple)
        if composite_traintuple.status == models.Status.waiting:
            self._worker.schedule_traintuple(composite_traintuple)
        return composite_traintuple

    def _add_aggregatetuple(
        self,
        key: str,
        spec: schemas.AggregatetupleSpec,
        spec_options: dict = None,
    ):
        # validation
        owner = self._check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.Algo, spec.algo_key)
        assert algo.category == schemas.AlgoCategory.aggregate

        in_tuples = list()
        in_permissions = list()
        for in_tuple_key in spec.in_models_keys:
            in_tuple = self._get_parent_task(in_tuple_key)

            if in_tuple.type_ == schemas.Type.Traintuple:
                permissions = in_tuple.train.model_permissions
            elif in_tuple.type_ == schemas.Type.Aggregatetuple:
                permissions = in_tuple.aggregate.model_permissions
            elif in_tuple.type_ == schemas.Type.CompositeTraintuple:
                permissions = in_tuple.composite.trunk_permissions

            in_permissions.append(permissions)
            in_tuples.append(in_tuple)

        if len(in_tuples) == 0:
            raise exceptions.EmptyInModelException("aggregatetuple needs in_model to aggregate")

        # Compute plan
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

        # Permissions
        public = False
        authorized_ids = set()
        for in_permission in in_permissions:
            if in_permission.process.public:
                public = True
            authorized_ids.update(in_permission.process.authorized_ids)

        aggregatetuple = models.Aggregatetuple(
            aggregate=models._Aggregate(
                model_permissions={"process": {"authorized_ids": list(authorized_ids), "public": public}},
                models=None,
            ),
            creation_date=self.__now(),
            key=key,
            category=models.TaskCategory.aggregate,
            algo=algo,
            owner=owner,
            worker=owner,
            compute_plan_key=compute_plan_key,
            rank=rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata if spec.metadata else dict(),
            parent_task_keys=spec.in_models_keys or list(),
        )
        aggregatetuple = self._db.add(aggregatetuple)
        if aggregatetuple.status == models.Status.waiting:
            self._worker.schedule_traintuple(aggregatetuple)
        return aggregatetuple

    def add(self, spec, spec_options=None):
        # find dynamically the method to call to create the asset
        method_name = f"_add_{spec.__class__.type_.value}"
        if spec.is_many():
            method_name += "s"
        add_asset = getattr(self, method_name)
        if spec.is_many():
            assets = add_asset(spec, spec_options)
            return [asset.key for asset in assets]
        else:
            key = spec.compute_key()
            asset = add_asset(key, spec, spec_options)
            if spec.__class__.type_ == schemas.Type.ComputePlan:
                return asset
            else:
                return key

    def link_dataset_with_data_samples(self, dataset_key, data_sample_keys):
        dataset = self._db.get(schemas.Type.Dataset, dataset_key)
        data_samples = list()
        for key in data_sample_keys:
            data_sample = self._db.get(schemas.Type.DataSample, key)
            if dataset_key not in data_sample.data_manager_keys:
                data_sample.data_manager_keys.append(dataset_key)
                if data_sample.test_only:
                    dataset.test_data_sample_keys.append(key)
                else:
                    dataset.train_data_sample_keys.append(key)
            else:
                logger.warning(f"Data sample already in dataset: {key}")
            data_samples.append(data_sample)
        return data_sample_keys

    def download(self, asset_type, url_field_path, key, destination):
        if self._db.is_local(key, asset_type):
            asset = self._db.get(type_=asset_type, key=key)
            # Get the field containing the path to the file.
            file_path = asset
            for field in url_field_path.split("."):
                file_path = getattr(file_path, field, None)
            # Copy the file to the destination folder
            shutil.copyfile(file_path, destination)
        else:
            self._db.remote_download(asset_type, url_field_path, key, destination)

    def download_model(self, key, destination_file):
        if self._db.is_local(key, schemas.Type.Model):
            asset = self._db.get(type_=schemas.Type.Model, key=key)
            shutil.copyfile(asset.address.storage_address, destination_file)
        else:
            self._db.remote_download_model(key, destination_file)

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

    def node_info(self):
        return {"type": "local backend"}

    def cancel_compute_plan(self, key):
        # Execution is synchronous in the local backend so this
        # function does not make sense.
        raise NotImplementedError

    def update_compute_plan(self, key: str, spec: schemas.UpdateComputePlanSpec, spec_options: dict = None):
        compute_plan = self._db.get(schemas.Type.ComputePlan, key)
        # Get all the new tuples and their dependencies
        (tuple_graph, traintuples, aggregatetuples, compositetuples) = compute_plan_module.get_dependency_graph(spec)

        # Get the rank of all the tuples already in the compute plan
        cp_traintuples = self.list(
            asset_type=schemas.Type.Traintuple,
            filters=[f"traintuple:compute_plan_key:{key}"],
        )
        cp_aggregatetuples = self.list(
            asset_type=schemas.Type.Aggregatetuple,
            filters=[f"aggregatetuple:compute_plan_key:{key}"],
        )
        cp_composite_traintuples = self.list(
            asset_type=schemas.Type.CompositeTraintuple,
            filters=[f"composite_traintuple:compute_plan_key:{key}"],
        )
        visited = dict()
        for tuple_ in cp_traintuples + cp_aggregatetuples + cp_composite_traintuples:
            visited[tuple_.key] = tuple_.rank

        # Update the tuple graph with the tuples already in the CP
        tuple_graph.update({k: list() for k in visited})
        visited = graph.compute_ranks(node_graph=tuple_graph, ranks=visited)

        compute_plan = self.__execute_compute_plan(
            spec, compute_plan, visited, traintuples, aggregatetuples, compositetuples, spec_options=dict()
        )
        return compute_plan
