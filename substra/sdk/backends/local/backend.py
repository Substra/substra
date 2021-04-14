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
import os
import shutil
import typing
import warnings
from distutils import util

import substra
from substra.sdk import schemas, models, exceptions, fs, graph, compute_plan as compute_plan_module
from substra.sdk.backends import base
from substra.sdk.backends.local import dal
from substra.sdk.backends.local import compute

_BACKEND_ID = "local-backend"
_MAX_LEN_KEY_METADATA = 50
_MAX_LEN_VALUE_METADATA = 100
DEBUG_OWNER = "debug_owner"


class Local(base.BaseBackend):
    def __init__(self, backend, *args, **kwargs):
        self._support_chainkeys = bool(util.strtobool(os.getenv("CHAINKEYS_ENABLED", 'False')))
        self._chainkey_dir = compute.LOCAL_DIR / "chainkeys"
        if self._support_chainkeys:
            print(f"Chainkeys support is on, the directory is {self._chainkey_dir}")
        # create a store to abstract the db
        self._db = dal.DataAccess(backend)
        self._worker = compute.Worker(
            self._db,
            support_chainkeys=self._support_chainkeys,
            chainkey_dir=self._chainkey_dir
        )

    @property
    def temp_directory(self):
        """Get the temporary directory where the assets are saved.
        The directory is deleted at the end of the execution."""
        return self._db.tmp_dir

    def login(self, username, password):
        self._db.login(username, password)

    def get(self, asset_type, key):
        return self._db.get(asset_type, key)

    def list(self, asset_type, filters=None):
        """List the assets

        This is a simplified version of the backend 'list' function,
        with limited support for filters.

        The format of the filters is 'asset_type:field_name:field_value',
        the function returns the assets whose fields equal those values.
        It does not support more advanced filtering methods.

        Args:
            asset_type (schemas.Type): Type of asset to return
            filters (str, optional): Filter the list of results. Defaults to None.

        Returns:
            typing.List[models._BaseModel]: List of results
        """
        db_assets = self._db.list(asset_type, filters=filters)
        # Parse the filters
        parsed_filters = dict()
        if filters is not None:
            for filter_ in filters:
                splitted = filter_.split(':')
                field_name = splitted[1]
                field_value = ''.join(splitted[2:])
                parsed_filters[field_name] = field_value
        # Filter the list of assets
        result = list()
        for asset in db_assets:
            # the filters use the 'response' (ie camel case) format
            if all([getattr(asset, key) == value for key, value in parsed_filters.items()]):
                result.append(asset)
        return result

    @staticmethod
    def _check_metadata(metadata: typing.Optional[typing.Dict[str, str]]):
        if metadata is not None:
            if any([len(key) > _MAX_LEN_KEY_METADATA for key in metadata]):
                raise exceptions.InvalidRequest(
                    "The key in metadata cannot be more than 50 characters",
                    400
                )
            if any([
                len(value) > _MAX_LEN_VALUE_METADATA or len(value) == 0
                for value in metadata.values()
            ]):
                raise exceptions.InvalidRequest(
                    "Values in metadata cannot be empty or more than 100 characters",
                    400
                )

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
        traintuple_keys=None,
        composite_traintuple_keys=None,
        aggregatetuple_keys=None,
        testtuple_keys=None,
    ):
        tuple_count = sum([
            len(x) for x in [
                traintuple_keys or list(),
                composite_traintuple_keys or list(),
                aggregatetuple_keys or list(),
                testtuple_keys or list(),
            ]
        ])
        key = self._db.get_local_key(schemas._Spec.compute_key())
        compute_plan = models.ComputePlan(
            key=key,
            status=models.Status.waiting,
            traintuple_keys=traintuple_keys,
            composite_traintuple_keys=composite_traintuple_keys,
            aggregatetuple_keys=aggregatetuple_keys,
            testtuple_keys=testtuple_keys,
            id_to_key=dict(),
            tag="",
            tuple_count=tuple_count,
            done_count=0,
            metadata=dict(),
        )
        return self._db.add(compute_plan)

    def __create_compute_plan_from_tuple(self, spec, key, in_tuples):
        # compute plan and rank
        if not spec.compute_plan_key and spec.rank == 0:
            #  Create a compute plan
            compute_plan = self.__add_compute_plan(traintuple_keys=[key])
            rank = 0
            compute_plan_key = compute_plan.key
        elif not spec.compute_plan_key and spec.rank is not None:
            raise substra.sdk.exceptions.InvalidRequest(
                "invalid inputs, a new ComputePlan should have a rank 0", 400
            )
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
                        [
                            in_tuple.rank
                            for in_tuple in in_tuples
                            if in_tuple.compute_plan_key == compute_plan_key
                        ]
                    )

            # Add to the compute plan
            list_keys = getattr(compute_plan, spec.compute_plan_attr_name)
            if list_keys is None:
                list_keys = list()
            list_keys.append(key)
            setattr(compute_plan, spec.compute_plan_attr_name, list_keys)

            compute_plan.tuple_count += 1
            compute_plan.status = models.Status.waiting

        else:
            compute_plan_key = ""
            rank = 0

        return compute_plan_key, rank

    def __get_id_rank_in_compute_plan(self, type_, key, id_to_key):
        tuple_ = self._db.get(type_, key)
        id_ = next((k for k in id_to_key if id_to_key[k] == key), None)
        return id_, tuple_.rank

    def __execute_compute_plan(
                self,
                spec,
                compute_plan,
                visited,
                traintuples,
                aggregatetuples,
                compositetuples,
                spec_options
            ):
        for id_, rank in sorted(visited.items(), key=lambda item: item[1]):
            if id_ in traintuples:
                traintuple = traintuples[id_]
                traintuple_spec = schemas.TraintupleSpec.from_compute_plan(
                    compute_plan_key=compute_plan.key,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=traintuple
                )
                traintuple_key = self.add(traintuple_spec, spec_options)
                compute_plan.id_to_key[id_] = traintuple_key

            elif id_ in aggregatetuples:
                aggregatetuple = aggregatetuples[id_]
                aggregatetuple_spec = schemas.AggregatetupleSpec.from_compute_plan(
                    compute_plan_key=compute_plan.key,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=aggregatetuple
                )
                aggregatetuple_key = self.add(
                    aggregatetuple_spec,
                    spec_options,
                )
                compute_plan.id_to_key[id_] = aggregatetuple_key

            elif id_ in compositetuples:
                compositetuple = compositetuples[id_]
                compositetuple_spec = schemas.CompositeTraintupleSpec.from_compute_plan(
                    compute_plan_key=compute_plan.key,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=compositetuple
                )
                compositetuple_key = self.add(
                    compositetuple_spec,
                    spec_options,
                )
                compute_plan.id_to_key[id_] = compositetuple_key

        if spec.testtuples:
            for testtuple in spec.testtuples:
                testtuple_spec = schemas.TesttupleSpec.from_compute_plan(
                    id_to_key=compute_plan.id_to_key,
                    spec=testtuple
                )
                self.add(testtuple_spec, spec_options)

        return compute_plan

    def __format_for_leaderboard(self, testtuple):
        traintuple = self._db.get(testtuple.traintuple_type, testtuple.traintuple_key)
        algo = self._db.get(traintuple.algo_type, traintuple.algo.key)
        return {
            'algo': {
                'key': algo.key,
                'checksum': algo.content.checksum,
                'name': algo.name,
                'storage_address': str(algo.content.storage_address)
            },
            'creator': testtuple.creator,
            'key': testtuple.key,
            'perf': testtuple.dataset.perf,
            'tag': testtuple.tag,
            'traintuple_key': testtuple.traintuple_key
        }

    def __check_same_data_manager(self, data_manager_key, data_sample_keys):
        """Check that all data samples are linked to this data manager"""
        # If the dataset is remote: the backend does not return the datasets
        # linked to each sample, so no check (already done in the backend).
        if self._db.is_local(data_manager_key):
            same_data_manager = all(
                [
                    data_manager_key
                    in self._db.get(schemas.Type.DataSample, key).data_manager_keys
                    for key in (data_sample_keys or list())
                ]
            )
            if not same_data_manager:
                raise substra.exceptions.InvalidRequest(
                    "dataSample do not belong to the same dataManager", 400
                )

    def __add_algo(self, model_class, key, spec, owner, spec_options=None):

        permissions = self.__compute_permissions(spec.permissions, owner)
        algo_file_path = self._db.save_file(spec.file, key)
        algo_description_path = self._db.save_file(spec.description, key)
        algo = model_class(
            key=key,
            name=spec.name,
            owner=owner,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            content={
                "checksum": fs.hash_file(algo_file_path),
                "storage_address": algo_file_path
            },
            description={
                "checksum": fs.hash_file(algo_description_path),
                "storage_address": algo_description_path
            },
            metadata=spec.metadata if spec.metadata else dict(),
        )
        return self._db.add(algo)

    def _add_algo(self, key, spec, spec_options=None):
        owner = self._check_metadata(spec.metadata)
        return self.__add_algo(models.Algo, key, spec, owner, spec_options=spec_options)

    def _add_aggregate_algo(self, key, spec, spec_options=None):
        owner = self._check_metadata(spec.metadata)
        return self.__add_algo(
            models.AggregateAlgo, key, spec, owner, spec_options=spec_options
        )

    def _add_composite_algo(self, key, spec, spec_options=None):
        owner = self._check_metadata(spec.metadata)
        return self.__add_algo(
            models.CompositeAlgo, key, spec, owner, spec_options=spec_options
        )

    def _add_dataset(self, key, spec, spec_options=None):

        owner = self._check_metadata(spec.metadata)

        permissions = self.__compute_permissions(spec.permissions, owner)

        dataset_file_path = self._db.save_file(spec.data_opener, key)
        dataset_description_path = self._db.save_file(spec.description, key)
        asset = models.Dataset(
            key=key,
            owner=owner,
            name=spec.name,
            objective_key=spec.objective_key if spec.objective_key else "",
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            type=spec.type,
            train_data_sample_keys=list(),
            test_data_sample_keys=list(),
            opener={
                "checksum": fs.hash_file(dataset_file_path),
                "storage_address": dataset_file_path
            },
            description={
                "checksum": fs.hash_file(dataset_description_path),
                "storage_address": dataset_description_path
            },
            metadata=spec.metadata if spec.metadata else dict(),
        )
        return self._db.add(asset)

    def _add_data_sample(self, key, spec, spec_options=None):
        if len(spec.data_manager_keys) == 0:
            raise exceptions.InvalidRequest(
                "Please add at least one data manager for the data sample",
                400
            )
        datasets = [
            self._db.get(schemas.Type.Dataset, dataset_key)
            for dataset_key in spec.data_manager_keys
        ]

        data_sample_file_path = self._db.save_file(spec.path, key)
        data_sample = models.DataSample(
            key=key,
            owner=_BACKEND_ID,
            path=data_sample_file_path,
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
            key = self._db.get_local_key(data_sample_spec.compute_key())
            data_sample = self._add_data_sample(
                key,
                data_sample_spec,
                spec_options,
            )
            data_samples.append(data_sample)
        return data_samples

    def _add_objective(self, key, spec, spec_options):

        owner = self._check_metadata(spec.metadata)
        permissions = self.__compute_permissions(spec.permissions, owner)

        # validate spec
        test_dataset = None
        if spec.test_data_manager_key:
            dataset = self._db.get(schemas.Type.Dataset, spec.test_data_manager_key)
            # validate test data samples
            if spec.test_data_sample_keys is None:
                spec.test_data_sample_keys = list()
            self.__check_same_data_manager(spec.test_data_manager_key, spec.test_data_sample_keys)

            test_dataset = {
                "data_manager_key": spec.test_data_manager_key,
                "data_sample_keys": spec.test_data_sample_keys,
                "metadata": dataset.metadata,
                "worker": dataset.owner,
            }
            if not dataset.objective_key:
                dataset.objective_key = key
            else:
                raise substra.exceptions.InvalidRequest(
                    "dataManager is already associated with a objective", 400
                )

        # Copy files to the local dir
        objective_file_path = self._db.save_file(spec.metrics, key)
        objective_description_path = self._db.save_file(spec.description, key)

        # create objective model instance
        objective = models.Objective(
            key=key,
            name=spec.name,
            owner=owner,
            test_dataset=test_dataset,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            description={
                "checksum": fs.hash_file(objective_description_path),
                "storage_address": objective_description_path
            },
            metrics={
                "name": spec.metrics_name,
                "checksum": fs.hash_file(objective_file_path),
                "storage_address": objective_file_path
            },
            metadata=spec.metadata if spec.metadata else dict(),
        )

        # add objective to storage and update optionnally the associated dataset
        objective = self._db.add(objective)

        return objective

    def _add_compute_plan(
        self,
        key: str,
        spec: schemas.ComputePlanSpec,
        spec_options: dict = None
    ):
        if spec.clean_models:
            warnings.warn(
                "'clean_models=True' is not supported on the local backend."
            )
        self._check_metadata(spec.metadata)
        # Get all the tuples and their dependencies
        (
            tuple_graph,
            traintuples,
            aggregatetuples,
            compositetuples
        ) = compute_plan_module.get_dependency_graph(spec)

        # Define the rank of each traintuple, aggregate tuple and composite tuple
        visited = graph.compute_ranks(node_graph=tuple_graph)

        compute_plan = models.ComputePlan(
            key=key,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata or dict(),
            id_to_key=dict(),
            tuple_count=0,
            done_count=0
        )
        compute_plan = self._db.add(compute_plan)

        # go through the tuples sorted by rank
        compute_plan = self.__execute_compute_plan(
            spec,
            compute_plan,
            visited,
            traintuples,
            aggregatetuples,
            compositetuples,
            spec_options
        )
        return compute_plan

    def _add_traintuple(self, key, spec, spec_options=None):
        # validation
        owner = self._check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.Algo, spec.algo_key)
        data_manager = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        in_traintuples = (
            [self._db.get(schemas.Type.Traintuple, key) for key in spec.in_models_keys]
            if spec.in_models_keys is not None
            else []
        )
        self.__check_same_data_manager(spec.data_manager_key, spec.train_data_sample_keys)

        # permissions
        with_permissions = [algo, data_manager] + in_traintuples

        public = True
        authorized_ids = None
        for element in with_permissions:
            public = public and element.permissions.process.public
            if not element.permissions.process.public:
                if authorized_ids is None:
                    authorized_ids = set(element.permissions.process.authorized_ids)
                else:
                    authorized_ids = set.intersection(
                        authorized_ids, set(element.permissions.process.authorized_ids)
                    )
        if public or authorized_ids is None:
            authorized_ids = list()
        else:
            authorized_ids = list(authorized_ids)

        # compute plan and rank
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(
            spec=spec,
            key=key,
            in_tuples=in_traintuples
        )

        # create model
        options = {}
        traintuple = models.Traintuple(
            key=key,
            creator=owner,
            algo={
                "key": spec.algo_key,
                "checksum": algo.content.checksum,
                "name": algo.name,
                "storage_address": algo.content.storage_address
            },
            dataset={
                "key": spec.data_manager_key,
                "opener_checksum": data_manager.opener.checksum,
                "data_sample_keys": spec.train_data_sample_keys,
                "worker": data_manager.owner,
                "metadata": {}
            },
            permissions={
                "process": {"public": public, "authorized_ids": authorized_ids},
            },
            log="",
            compute_plan_key=compute_plan_key,
            rank=rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            in_models=[
                {
                    "key": in_traintuple.out_model.key,
                    "checksum": in_traintuple.out_model.checksum,
                    "storage_address": in_traintuple.out_model.storage_address,
                    "traintuple_key": in_traintuple.key,
                }
                for in_traintuple in in_traintuples
            ],
            metadata=spec.metadata if spec.metadata else dict(),
            **options,
        )

        traintuple = self._db.add(traintuple)
        self._worker.schedule_traintuple(traintuple)
        return traintuple

    def _add_testtuple(self, key, spec, spec_options=None):

        # validation
        owner = self._check_metadata(spec.metadata)
        objective = self._db.get(schemas.Type.Objective, spec.objective_key)

        traintuple = None
        for tuple_type in [
                schemas.Type.Traintuple,
                schemas.Type.CompositeTraintuple,
                schemas.Type.Aggregatetuple
        ]:
            try:
                traintuple = self._db.get(tuple_type, spec.traintuple_key, log=False)
                break
            except exceptions.NotFound:
                pass
        if not traintuple:
            raise exceptions.NotFound(f"Wrong pk {spec.traintuple_key}", 404)

        if traintuple.status in [models.Status.failed, models.Status.canceled]:
            raise substra.exceptions.InvalidRequest(
                f"could not register this testtuple, \
                the traintuple {traintuple.key} has a status {traintuple.status}",
                400,
            )
        if spec.data_manager_key is not None:
            self._db.get(schemas.Type.Dataset, spec.data_manager_key)
            if spec.test_data_sample_keys is not None:
                self.__check_same_data_manager(spec.data_manager_key, spec.test_data_sample_keys)

        # create model
        # if dataset is not defined, take it from objective
        if spec.data_manager_key:
            assert (
                spec.test_data_sample_keys is not None
                and len(spec.test_data_sample_keys) > 0
            )
            dataset_key = spec.data_manager_key
            test_data_sample_keys = spec.test_data_sample_keys
            certified = (
                objective.test_dataset is not None
                and objective.test_dataset.data_manager_key == spec.data_manager_key
                and set(objective.test_dataset.data_sample_keys)
                == set(spec.test_data_sample_keys)
            )
        else:
            assert (
                objective.test_dataset
            ), "can not create a certified testtuple, no data associated with objective"
            dataset_key = objective.test_dataset.data_manager_key
            test_data_sample_keys = objective.test_dataset.data_sample_keys
            certified = True

        dataset = self._db.get(schemas.Type.Dataset, dataset_key)

        if traintuple.compute_plan_key:
            compute_plan = self._db.get(
                schemas.Type.ComputePlan, traintuple.compute_plan_key
            )
            if compute_plan.testtuple_keys is None:
                compute_plan.testtuple_keys = [key]
            else:
                compute_plan.testtuple_keys.append(key)
            compute_plan.tuple_count += 1
            compute_plan.status = models.Status.waiting

        options = {}
        testtuple = models.Testtuple(
            key=key,
            creator=owner,
            objective={
                "key": spec.objective_key,
                "metrics": objective.metrics
            },
            traintuple_key=spec.traintuple_key,
            traintuple_type=traintuple.type_.value,
            algo=traintuple.algo,
            certified=certified,
            dataset={
                "key": dataset_key,
                "opener_checksum": dataset.opener.checksum,
                "perf": -1,
                "data_sample_keys": test_data_sample_keys,
                "worker": dataset.owner,
            },
            log="",
            tag=spec.tag or "",
            status=models.Status.waiting,
            rank=traintuple.rank,
            compute_plan_key=traintuple.compute_plan_key,
            metadata=spec.metadata if spec.metadata else dict(),
            **options,
        )
        testtuple = self._db.add(testtuple)
        self._worker.schedule_testtuple(testtuple)
        return testtuple

    def _add_composite_traintuple(
        self,
        key: str,
        spec: schemas.CompositeTraintupleSpec,
        spec_options=None
    ):
        # validation
        owner = self._check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.CompositeAlgo, spec.algo_key)
        dataset = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        self.__check_same_data_manager(spec.data_manager_key, spec.train_data_sample_keys)

        in_head_model = None
        in_trunk_model = None
        in_tuples = list()

        if spec.in_head_model_key:
            in_head_tuple = self._db.get(schemas.Type.CompositeTraintuple, spec.in_head_model_key)
            assert in_head_tuple.out_head_model
            in_head_model = models.InHeadModel(
                key=in_head_tuple.out_head_model.out_model.key,
                checksum=in_head_tuple.out_head_model.out_model.checksum,
                storage_address=in_head_tuple.out_head_model.out_model.storage_address
            )
            in_tuples.append(in_head_tuple)

        if spec.in_trunk_model_key:
            try:
                # in trunk model is a composite traintuple out trunk model
                in_trunk_tuple = self._db.get(
                    schemas.Type.CompositeTraintuple, spec.in_trunk_model_key, log=False
                )
                assert in_trunk_tuple.out_trunk_model
                in_model = in_trunk_tuple.out_trunk_model.out_model
            except exceptions.NotFound:
                # in trunk model is an aggregate tuple out model
                in_trunk_tuple = self._db.get(schemas.Type.Aggregatetuple, spec.in_trunk_model_key)
                assert in_trunk_tuple.out_model
                in_model = in_trunk_tuple.out_model

            in_trunk_model = models.InModel(
                key=in_model.key,
                checksum=in_model.checksum,
                storage_address=in_model.storage_address
            )
            in_tuples.append(in_trunk_tuple)

        # Compute plan
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

        # permissions
        trunk_model_permissions = schemas.Permissions(
            public=False,
            authorized_ids=spec.out_trunk_model_permissions.authorized_ids
        )
        trunk_model_permissions = self.__compute_permissions(trunk_model_permissions)

        if spec.in_head_model_key:
            head_model_permissions = in_head_tuple.out_head_model.permissions
        else:
            head_model_permissions = {
                "process": {
                    "public": False,
                    "authorized_ids": [owner]
                }
            }

        composite_traintuple = models.CompositeTraintuple(
            key=key,
            creator=owner,
            algo={
                "key": spec.algo_key,
                "checksum": algo.content.checksum,
                "name": algo.name,
                "storage_address": algo.content.storage_address
            },
            dataset={
                "key": spec.data_manager_key,
                "opener_checksum": dataset.opener.checksum,
                "data_sample_keys": spec.train_data_sample_keys,
                "worker": dataset.owner,
            },
            tag=spec.tag or '',
            compute_plan_key=compute_plan_key,
            rank=rank,
            status=models.Status.waiting,
            log='',
            in_head_model=in_head_model,
            in_trunk_model=in_trunk_model,
            out_head_model={
                "permissions": head_model_permissions,
                "out_model": None
            },
            out_trunk_model={
                "permissions": {
                    "process": trunk_model_permissions.dict()
                },
                "out_model": None
            },
            metadata=spec.metadata or dict()
        )
        composite_traintuple = self._db.add(composite_traintuple)
        if composite_traintuple.status == models.Status.waiting:
            self._worker.schedule_traintuple(composite_traintuple)
        return composite_traintuple

    def _add_aggregatetuple(self,
                            key: str,
                            spec: schemas.AggregatetupleSpec,
                            spec_options: dict = None,
                            ):
        # validation
        owner = self._check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.AggregateAlgo, spec.algo_key)
        in_tuples = list()
        in_models = list()
        in_permissions = list()
        for model_key in spec.in_models_keys:
            try:
                in_tuple = self._db.get(schemas.Type.Traintuple, key=model_key, log=False)
                in_models.append({
                    "key": in_tuple.out_model.key,
                    "checksum": in_tuple.out_model.checksum,
                    "storage_address": in_tuple.out_model.storage_address,
                    "traintuple_key": in_tuple.key,
                })
                in_permissions.append(in_tuple.permissions.process)
            except exceptions.NotFound:
                in_tuple = self._db.get(schemas.Type.CompositeTraintuple, key=model_key)
                in_models.append({
                    "key": in_tuple.out_trunk_model.out_model.key,
                    "checksum": in_tuple.out_trunk_model.out_model.checksum,
                    "storage_address": in_tuple.out_trunk_model.out_model.storage_address,
                    "traintuple_key": in_tuple.key,
                })
                in_permissions.append(in_tuple.out_trunk_model.permissions.process)
            in_tuples.append(in_tuple)

        # Compute plan
        compute_plan_key, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

        # Permissions
        public = False
        authorized_ids = set()
        for in_permission in in_permissions:
            if in_permission.public:
                public = True
            authorized_ids.update(in_permission.authorized_ids)
        authorized_ids = list(authorized_ids)

        aggregatetuple = models.Aggregatetuple(
            key=key,
            creator=owner,
            worker=spec.worker,
            algo={
                "key": spec.algo_key,
                "checksum": algo.content.checksum,
                "name": algo.name,
                "storage_address": algo.content.storage_address
            },
            permissions={
                "process": {
                    "authorized_ids": authorized_ids,
                    "public": public
                }
            },
            tag=spec.tag or '',
            compute_plan_key=compute_plan_key,
            rank=rank,
            status=models.Status.waiting,
            log='',
            in_models=in_models,
            out_model=None,
            metadata=spec.metadata or dict()
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
            key = self._db.get_local_key(spec.compute_key())
            asset = add_asset(key, spec, spec_options)
            if spec.__class__.type_ == schemas.Type.ComputePlan:
                return asset
            else:
                return key

    def link_dataset_with_objective(self, dataset_key, objective_key):
        # validation
        dataset = self._db.get(schemas.Type.Dataset, dataset_key)
        self._db.get(schemas.Type.Objective, objective_key)
        if dataset.objective_key:
            raise substra.exceptions.InvalidRequest(
                "Dataset already linked to an objective", 400
            )

        dataset.objective_key = objective_key
        return dataset.key

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
                print(f"Data sample already in dataset: {key}")
            data_samples.append(data_sample)
        return data_sample_keys

    def download(self, asset_type, url_field_path, key, destination):
        if self._db.is_local(key):
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
        if self._db.is_local(key):
            asset = self._db.get(type_=schemas.Type.Model, key=key)
            shutil.copyfile(asset.storage_address, destination_file)
        else:
            self._db.remote_download_model(key, destination_file)

    def describe(self, asset_type, key):
        if self._db.is_local(key):
            asset = self._db.get(type_=asset_type, key=key)
            if not hasattr(asset, "description") or not asset.description:
                raise ValueError("This element does not have a description.")
            with open(asset.description.storage_address, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return self._db.get_remote_description(asset_type, key)

    def node_info(self):
        return {"type": "local backend"}

    def leaderboard(self, objective_key, sort='desc'):
        objective = self._db.get(schemas.Type.Objective, objective_key)
        testtuples = self._db.list(schemas.Type.Testtuple, filters=None)
        certified_testtuples = [
            self.__format_for_leaderboard(t)
            for t in testtuples
            if t.objective.key == objective_key and t.certified
        ]
        certified_testtuples.sort(key=lambda x: x['perf'], reverse=(sort == 'desc'))
        board = {
            'objective': objective.dict(exclude_none=False, by_alias=True),
            'testtuples': certified_testtuples
        }
        return board

    def cancel_compute_plan(self, key):
        # Execution is synchronous in the local backend so this
        # function does not make sense.
        raise NotImplementedError

    def update_compute_plan(self,
                            key: str,
                            spec: schemas.UpdateComputePlanSpec,
                            spec_options: dict = None):
        compute_plan = self._db.get(schemas.Type.ComputePlan, key)

        # Get all the new tuples and their dependencies
        (
            tuple_graph,
            traintuples,
            aggregatetuples,
            compositetuples
        ) = compute_plan_module.get_dependency_graph(spec)

        # Define the rank of each traintuple, aggregate tuple and composite tuple
        old_tuples = {id_: list() for id_ in compute_plan.id_to_key}
        tuple_graph.update(old_tuples)

        # Get the rank of all the tuples already in the compute plan
        visited = dict()
        if compute_plan.traintuple_keys:
            for key in compute_plan.traintuple_keys:
                id_, rank = self.__get_id_rank_in_compute_plan(
                    schemas.Type.Traintuple,
                    key,
                    compute_plan.id_to_key
                )
                visited[id_] = rank

        if compute_plan.aggregatetuple_keys:
            for key in compute_plan.aggregatetuple_keys:
                id_, rank = self.__get_id_rank_in_compute_plan(
                    schemas.Type.Aggregatetuple,
                    key,
                    compute_plan.id_to_key
                )
                visited[id_] = rank

        if compute_plan.composite_traintuple_keys:
            for key in compute_plan.composite_traintuple_keys:
                id_, rank = self.__get_id_rank_in_compute_plan(
                    schemas.Type.CompositeTraintuple,
                    key,
                    compute_plan.id_to_key
                )
                visited[id_] = rank

        visited = graph.compute_ranks(node_graph=tuple_graph, ranks=visited)

        compute_plan = self.__execute_compute_plan(
            spec,
            compute_plan,
            visited,
            traintuples,
            aggregatetuples,
            compositetuples,
            spec_options=dict()
        )
        return compute_plan
