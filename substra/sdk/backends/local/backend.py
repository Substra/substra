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
import shutil
import typing
import uuid

import substra
from substra.sdk import schemas, exceptions, utils
from substra.sdk.backends import base
from substra.sdk.backends.local import models
from substra.sdk.backends.local import db
from substra.sdk.backends.local import fs
from substra.sdk.backends.local import hasher
from substra.sdk.backends.local import compute

_BACKEND_ID = "local-backend"


class Local(base.BaseBackend):
    def __init__(self, *args, **kwargs):
        # create a store to abstract the db
        self._db = db.get()
        self._worker = compute.Worker()

    def get(self, asset_type, key):
        return self._db.get(asset_type, key).to_response()

    def list(self, asset_type, filters=None):
        db_assets = self._db.list(asset_type)
        if filters is None:
            filters = list()
        filters = {
            filter_.split(':')[1]: ''.join(filter_.split(':')[2:])
            for filter_ in filters
        }
        assets = [
            a.to_response() for a in db_assets
            if all([
                a.to_response().get(key, None) == value for key, value in filters.items()
            ])
        ]
        return assets

    @staticmethod
    def __check_metadata(metadata: typing.Optional[typing.Dict[str, str]]):
        if metadata is not None:
            if any([len(key) > 50 for key in metadata]):
                raise exceptions.InvalidRequest(
                    "The key in metadata cannot be more than 50 characters",
                    400
                )
            if any([len(value) > 100 or len(value) == 0 for value in metadata.values()]):
                raise exceptions.InvalidRequest(
                    "Values in metadata cannot be empty or more than 100 characters",
                    400
                )

    @staticmethod
    def __compute_permissions(permissions):
        """Compute the permissions

        If the permissions are private, the active node is
        in the authorized ids.
        """
        if permissions.public:
            permissions.authorized_ids = list()
        elif not permissions.public and _BACKEND_ID not in permissions.authorized_ids:
            permissions.authorized_ids.append(_BACKEND_ID)
        return permissions

    def __add_compute_plan(
        self,
        traintuple_keys=None,
        composite_traintuple_keys=None,
        aggregatetuple_keys=None,
        testtuple_keys=None,
    ):
        tuple_count = sum([
            (len(x) if x else 0) for x in [
                traintuple_keys,
                composite_traintuple_keys,
                aggregatetuple_keys,
                testtuple_keys,
            ]
        ])
        compute_plan = models.ComputePlan(
            compute_plan_id=uuid.uuid4().hex,
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
        if not spec.compute_plan_id and spec.rank == 0:
            #  Create a compute plan
            compute_plan = self.__add_compute_plan(traintuple_keys=[key])
            rank = 0
            compute_plan_id = compute_plan.compute_plan_id
        elif not spec.compute_plan_id and spec.rank is not None:
            raise substra.sdk.exceptions.InvalidRequest(
                "invalid inputs, a new ComputePlan should have a rank 0", 400
            )
        elif spec.compute_plan_id:
            compute_plan = self._db.get(schemas.Type.ComputePlan, spec.compute_plan_id)
            compute_plan_id = compute_plan.compute_plan_id
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
                            if in_tuple.compute_plan_id == compute_plan_id
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
            compute_plan_id = ""
            rank = 0

        return compute_plan_id, rank

    def __get_all_tuples_compute_plan(self, spec: schemas.UpdateComputePlanSpec):
        all_tuples = dict()
        traintuples = dict()
        if spec.traintuples:
            for traintuple in spec.traintuples:
                if traintuple.in_models_ids is not None:
                    all_tuples[traintuple.traintuple_id] = traintuple.in_models_ids
                else:
                    all_tuples[traintuple.traintuple_id] = list()
                traintuples[traintuple.traintuple_id] = traintuple

        aggregatetuples = dict()
        if spec.aggregatetuples:
            for aggregatetuple in spec.aggregatetuples:
                if aggregatetuple.in_models_ids is not None:
                    all_tuples[aggregatetuple.aggregatetuple_id] = aggregatetuple.in_models_ids
                else:
                    all_tuples[aggregatetuple.aggregatetuple_id] = list()
                aggregatetuples[aggregatetuple.aggregatetuple_id] = aggregatetuple

        compositetuples = dict()
        if spec.composite_traintuples:
            for compositetuple in spec.composite_traintuples:
                assert not compositetuple.out_trunk_model_permissions.public
                all_tuples[compositetuple.composite_traintuple_id] = list()
                if compositetuple.in_head_model_id is not None:
                    all_tuples[compositetuple.composite_traintuple_id].append(
                        compositetuple.in_head_model_id
                    )
                if compositetuple.in_trunk_model_id is not None:
                    all_tuples[compositetuple.composite_traintuple_id].append(
                        compositetuple.in_trunk_model_id
                    )
                compositetuples[compositetuple.composite_traintuple_id] = compositetuple

        return all_tuples, traintuples, aggregatetuples, compositetuples

    def __get_id_rank_in_compute_plan(self, type_, key, id_to_key):
        tuple_ = self._db.get(schemas.Type.Traintuple, key)
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
            exist_ok,
            spec_options
            ):
        for id_, rank in sorted(visited.items(), key=lambda item: item[1]):
            if id_ in traintuples:
                traintuple = traintuples[id_]
                traintuple_spec = schemas.TraintupleSpec.from_compute_plan(
                    compute_plan_id=compute_plan.compute_plan_id,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=traintuple
                )
                traintuple = self.add(traintuple_spec, exist_ok, spec_options)
                compute_plan.id_to_key[id_] = traintuple["key"]

            elif id_ in aggregatetuples:
                aggregatetuple = aggregatetuples[id_]
                aggregatetuple_spec = schemas.AggregatetupleSpec.from_compute_plan(
                    compute_plan_id=compute_plan.compute_plan_id,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=aggregatetuple
                )
                aggregatetuple = self.add(aggregatetuple_spec, exist_ok, spec_options)
                compute_plan.id_to_key[id_] = aggregatetuple["key"]

            elif id_ in compositetuples:
                compositetuple = compositetuples[id_]
                compositetuple_spec = schemas.CompositeTraintupleSpec.from_compute_plan(
                    compute_plan_id=compute_plan.compute_plan_id,
                    id_to_key=compute_plan.id_to_key,
                    rank=rank,
                    spec=compositetuple
                )
                compositetuple = self.add(compositetuple_spec, exist_ok, spec_options)
                compute_plan.id_to_key[id_] = compositetuple["key"]

        if spec.testtuples:
            for testtuple in spec.testtuples:
                testtuple_spec = schemas.TesttupleSpec.from_compute_plan(
                    id_to_key=compute_plan.id_to_key,
                    spec=testtuple
                )
                testtuple = self.add(testtuple_spec, exist_ok, spec_options)

        return compute_plan

    def __format_for_leaderboard(self, testtuple):
        for tuple_type in [
                schemas.Type.Traintuple,
                schemas.Type.CompositeTraintuple,
                schemas.Type.Aggregatetuple
        ]:
            try:
                traintuple = self._db.get(tuple_type, testtuple.traintuple_key)
                break
            except exceptions.NotFound:
                pass
        algo = self._db.get(traintuple.algo_type, traintuple.algo_key)
        return {
            'algo': {
                'hash': algo.key,
                'name': algo.name,
                'storageAddress': str(algo.file)
            },
            'creator': testtuple.creator,
            'key': testtuple.key,
            'perf': testtuple.dataset.perf,
            'tag': testtuple.tag,
            'traintupleKey': testtuple.traintuple_key
        }

    def __check_same_data_manager(self, data_manager_key, data_sample_keys):
        """Check that all data samples are linked to this data manager"""
        same_data_manager = all(
            [
                data_manager_key
                in self._db.get(schemas.Type.DataSample, key).data_manager_keys
                for key in data_sample_keys
            ]
        )
        if not same_data_manager:
            raise substra.exceptions.InvalidRequest(
                "dataSample do not belong to the same dataManager", 400
            )

    def __add_algo(self, model_class, spec, exist_ok, spec_options=None):
        permissions = self.__compute_permissions(spec.permissions)
        algo = model_class(
            key=fs.hash_file(spec.file),
            pkhash=fs.hash_file(spec.file),
            name=spec.name,
            owner=_BACKEND_ID,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            file=str(spec.file),
            description=str(spec.description),
            metadata=spec.metadata if spec.metadata else dict(),
        )
        return self._db.add(algo, exist_ok)

    def _add_algo(self, spec, exist_ok, spec_options=None):
        self.__check_metadata(spec.metadata)
        return self.__add_algo(models.Algo, spec, exist_ok, spec_options=spec_options)

    def _add_aggregate_algo(self, spec, exist_ok, spec_options=None):
        self.__check_metadata(spec.metadata)
        return self.__add_algo(
            models.AggregateAlgo, spec, exist_ok, spec_options=spec_options
        )

    def _add_composite_algo(self, spec, exist_ok, spec_options=None):
        self.__check_metadata(spec.metadata)
        return self.__add_algo(
            models.CompositeAlgo, spec, exist_ok, spec_options=spec_options
        )

    def _add_dataset(self, spec, exist_ok, spec_options):
        self.__check_metadata(spec.metadata)
        permissions = self.__compute_permissions(spec.permissions)
        asset = models.Dataset(
            key=fs.hash_file(spec.data_opener),
            pkhash=fs.hash_file(spec.data_opener),
            owner=_BACKEND_ID,
            name=spec.name,
            objective_key=spec.objective_key if spec.objective_key else "",
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            type=spec.type,
            train_data_sample_keys=[],
            test_data_sample_keys=[],
            data_opener=str(spec.data_opener),
            description=str(spec.description),
            metadata=spec.metadata if spec.metadata else dict(),
        )
        return self._db.add(asset, exist_ok)

    def _add_data_sample(self, spec, exist_ok, spec_options):
        assert len(spec.data_manager_keys) > 0
        datasets = [
            self._db.get(schemas.Type.Dataset, dataset_key)
            for dataset_key in spec.data_manager_keys
        ]

        data_sample = models.DataSample(
            key=fs.hash_directory(spec.path),
            pkhash=fs.hash_directory(spec.path),
            owner=_BACKEND_ID,
            path=str(spec.path),
            data_manager_keys=spec.data_manager_keys,
            test_only=spec.test_only,
        )
        data_sample = self._db.add(data_sample, exist_ok)

        # update dataset(s) accordingly
        for dataset in datasets:
            if spec.test_only:
                samples_list = dataset.test_data_sample_keys
            else:
                samples_list = dataset.train_data_sample_keys
            if data_sample.key not in samples_list:
                samples_list.append(data_sample.key)

        return data_sample

    def _add_data_samples(self, spec, exist_ok, spec_options):
        datasets = [
            self._db.get(schemas.Type.Dataset, dataset_key)
            for dataset_key in spec.data_manager_keys
        ]

        data_samples = [
            models.DataSample(
                key=fs.hash_directory(str(p)),
                pkhash=fs.hash_directory(str(p)),
                owner=_BACKEND_ID,
                path=str(p),
                data_manager_keys=spec.data_manager_keys,
                test_only=spec.test_only,
            )
            for p in spec.paths
        ]

        data_samples = [self._db.add(a) for a in data_samples]

        # update dataset(s) accordingly
        for dataset in datasets:
            if spec.test_only:
                samples_list = dataset.test_data_sample_keys
            else:
                samples_list = dataset.train_data_sample_keys

            for data_sample in data_samples:
                if data_sample.key not in samples_list:
                    samples_list.append(data_sample.key)

        return data_samples

    def _add_objective(self, spec, exist_ok, spec_options):
        self.__check_metadata(spec.metadata)
        permissions = self.__compute_permissions(spec.permissions)
        objective_key = fs.hash_file(spec.metrics)

        # validate spec
        test_dataset = None
        if spec.test_data_manager_key:
            dataset = self._db.get(schemas.Type.Dataset, spec.test_data_manager_key)
            # validate test data samples
            if spec.test_data_sample_keys is None:
                spec.test_data_sample_keys = list()
            self.__check_same_data_manager(spec.test_data_manager_key, spec.test_data_sample_keys)

            test_dataset = {
                "dataset_key": spec.test_data_manager_key,
                "data_sample_keys": spec.test_data_sample_keys,
            }
            if not dataset.objective_key:
                dataset.objective_key = objective_key
            else:
                raise substra.exceptions.InvalidRequest(
                    "dataManager is already associated with a objective", 400
                )

        # create objective model instance
        objective = models.Objective(
            key=objective_key,
            pkhash=objective_key,
            name=spec.name,
            owner=_BACKEND_ID,
            test_dataset=test_dataset,
            permissions={
                "process": {
                    "public": permissions.public,
                    "authorized_ids": permissions.authorized_ids,
                },
            },
            description=str(spec.description),
            metrics=str(spec.metrics),
            metadata=spec.metadata if spec.metadata else dict(),
        )

        # add objective to storage and update optionnally the associated dataset
        objective = self._db.add(objective, exist_ok)

        return objective

    def _add_compute_plan(
        self,
        spec: schemas.ComputePlanSpec,
        exist_ok: bool,
        spec_options: dict = None
    ):
        if spec.clean_models:
            raise ValueError(
                "'clean_models=True' is not supported on the local backend."
            )
        self.__check_metadata(spec.metadata)
        # Get all the tuples and their dependencies
        (
            all_tuples,
            traintuples,
            aggregatetuples,
            compositetuples
        ) = self.__get_all_tuples_compute_plan(spec)

        # Define the rank of each traintuple, aggregate tuple and composite tuple
        visited = utils.compute_ranks(node_graph=all_tuples)

        compute_plan = models.ComputePlan(
            compute_plan_id=uuid.uuid4().hex,
            tag=spec.tag or "",
            status=models.Status.waiting,
            metadata=spec.metadata or dict(),
            id_to_key=dict(),
            tuple_count=0,
            done_count=0
        )
        compute_plan = self._db.add(compute_plan, exist_ok)

        # go through the tuples sorted by rank
        compute_plan = self.__execute_compute_plan(
            spec,
            compute_plan,
            visited,
            traintuples,
            aggregatetuples,
            compositetuples,
            exist_ok,
            spec_options
        )
        return compute_plan

    def _add_traintuple(self, spec, exist_ok, spec_options=None):
        # validation
        self.__check_metadata(spec.metadata)
        algo = self._db.get(schemas.Type.Algo, spec.algo_key)
        data_manager = self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        in_traintuples = (
            [self._db.get(schemas.Type.Traintuple, key) for key in spec.in_models_keys]
            if spec.in_models_keys is not None
            else []
        )
        self.__check_same_data_manager(spec.data_manager_key, spec.train_data_sample_keys)

        key_components = (
            [_BACKEND_ID, spec.algo_key, spec.data_manager_key]
            + spec.train_data_sample_keys
            + spec.in_models_keys
            if spec.in_models_keys is not None
            else []
        )
        key = hasher.Hasher(values=key_components).compute()

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
        compute_plan_id, rank = self.__create_compute_plan_from_tuple(
            spec=spec,
            key=key,
            in_tuples=in_traintuples
        )

        # create model
        options = {}
        traintuple = models.Traintuple(
            key=key,
            creator=_BACKEND_ID,
            worker=_BACKEND_ID,
            algo_key=spec.algo_key,
            dataset={
                "opener_hash": spec.data_manager_key,
                "keys": spec.train_data_sample_keys,
                "worker": _BACKEND_ID,
            },
            permissions={
                "process": {"public": public, "authorized_ids": authorized_ids},
            },
            log="",
            compute_plan_id=compute_plan_id,
            rank=rank,
            tag=spec.tag or "",
            status=models.Status.waiting,
            in_models=[
                {
                    "hash": in_traintuple.out_model.hash_,
                    "storage_address": in_traintuple.out_model.storage_address,
                }
                for in_traintuple in in_traintuples
            ],
            metadata=spec.metadata if spec.metadata else dict(),
            **options,
        )

        traintuple = self._db.add(traintuple, exist_ok)
        self._worker.schedule_traintuple(traintuple)
        return traintuple

    def _add_testtuple(self, spec, exist_ok, spec_options=None):
        # validation
        self.__check_metadata(spec.metadata)
        objective = self._db.get(schemas.Type.Objective, spec.objective_key)

        traintuple = None
        traintuple_type = None
        for tuple_type in [
                schemas.Type.Traintuple,
                schemas.Type.CompositeTraintuple,
                schemas.Type.Aggregatetuple
        ]:
            try:
                traintuple = self._db.get(tuple_type, spec.traintuple_key)
                traintuple_type = tuple_type
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

        # Hash creation
        key_components = [_BACKEND_ID, spec.objective_key, spec.traintuple_key]
        if spec.test_data_sample_keys is not None:
            key_components += spec.test_data_sample_keys
        if spec.data_manager_key is not None:
            key_components += spec.data_manager_key
        key = hasher.Hasher(values=key_components).compute()

        # create model
        # if dataset is not defined, take it from objective
        if spec.data_manager_key:
            assert (
                spec.test_data_sample_keys is not None
                and len(spec.test_data_sample_keys) > 0
            )
            dataset_opener = spec.data_manager_key
            test_data_sample_keys = spec.test_data_sample_keys
            certified = (
                objective.test_dataset is not None
                and objective.test_dataset.dataset_key == spec.data_manager_key
                and set(objective.test_dataset.data_sample_keys)
                == set(spec.test_data_sample_keys)
            )
        else:
            assert (
                objective.test_dataset
            ), "can not create a certified testtuple, no data associated with objective"
            dataset_opener = objective.test_dataset.dataset_key
            test_data_sample_keys = objective.test_dataset.data_sample_keys
            certified = True

        if traintuple.compute_plan_id:
            compute_plan = self._db.get(
                schemas.Type.ComputePlan, traintuple.compute_plan_id
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
            creator=_BACKEND_ID,
            objective_key=spec.objective_key,
            traintuple_key=spec.traintuple_key,
            certified=certified,
            dataset={
                "opener_hash": dataset_opener,
                "perf": -1,
                "keys": test_data_sample_keys,
                "worker": _BACKEND_ID,
            },
            log="",
            tag=spec.tag or "",
            status=models.Status.waiting,
            rank=traintuple.rank,
            compute_plan_id=traintuple.compute_plan_id,
            metadata=spec.metadata if spec.metadata else dict(),
            **options,
        )
        testtuple = self._db.add(testtuple, exist_ok)
        self._worker.schedule_testtuple(testtuple, traintuple_type)
        return testtuple

    def _add_composite_traintuple(
        self,
        spec: schemas.CompositeTraintupleSpec,
        exist_ok: bool,
        spec_options=None
    ):
        # validation
        self.__check_metadata(spec.metadata)
        self._db.get(schemas.Type.CompositeAlgo, spec.algo_key)
        self._db.get(schemas.Type.Dataset, spec.data_manager_key)
        self.__check_same_data_manager(spec.data_manager_key, spec.train_data_sample_keys)

        in_head_model = None
        in_trunk_model = None
        in_tuples = list()

        if spec.in_head_model_key:
            in_head_tuple = self._db.get(schemas.Type.CompositeTraintuple, spec.in_head_model_key)
            assert in_head_tuple.out_head_model
            in_head_model = models.InModel(
                hash=in_head_tuple.out_head_model.out_model.hash_,
                storage_address=in_head_tuple.out_head_model.out_model.storage_address
            )
            in_tuples.append(in_head_tuple)

        if spec.in_trunk_model_key:
            try:
                # in trunk model is a composite traintuple out trunk model
                in_trunk_tuple = self._db.get(
                    schemas.Type.CompositeTraintuple, spec.in_trunk_model_key
                )
                assert in_trunk_tuple.out_trunk_model
                in_model = in_trunk_tuple.out_trunk_model.out_model
            except exceptions.NotFound:
                # in trunk model is an aggregate tuple out model
                in_trunk_tuple = self._db.get(schemas.Type.Aggregatetuple, spec.in_trunk_model_key)
                assert in_trunk_tuple.out_model
                in_model = in_trunk_tuple.out_model

            in_trunk_model = models.InModel(
                hash=in_model.hash_,
                storage_address=in_model.storage_address
            )
            in_tuples.append(in_trunk_tuple)

        # Hash key
        #  * has the same `algo_key`, `data_manager_key`, `train_data_sample_keys`,
        #  `in_head_models_key` and `in_trunk_model_key`
        key_components = [spec.algo_key, spec.data_manager_key] + spec.train_data_sample_keys
        if spec.in_head_model_key:
            key_components.append(spec.in_head_model_key)
        if spec.in_trunk_model_key:
            key_components.append(spec.in_trunk_model_key)
        key = hasher.Hasher(values=key_components).compute()

        # Compute plan
        compute_plan_id, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

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
                    "authorized_ids": [_BACKEND_ID]
                }
            }

        composite_traintuple = models.CompositeTraintuple(
            key=key,
            creator=_BACKEND_ID,
            worker=_BACKEND_ID,
            algo_key=spec.algo_key,
            dataset={
                "opener_hash": spec.data_manager_key,
                "keys": spec.train_data_sample_keys,
                "worker": _BACKEND_ID,
            },
            tag=spec.tag or '',
            compute_plan_id=compute_plan_id,
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
        composite_traintuple = self._db.add(composite_traintuple, exist_ok)
        if composite_traintuple.status == models.Status.waiting:
            self._worker.schedule_traintuple(composite_traintuple)
        return composite_traintuple

    def _add_aggregatetuple(self,
                            spec: schemas.AggregatetupleSpec,
                            exist_ok: bool,
                            spec_options: dict = None,
                            ):
        # validation
        self.__check_metadata(spec.metadata)
        self._db.get(schemas.Type.AggregateAlgo, spec.algo_key)
        in_tuples = list()
        in_models = list()
        in_permissions = list()
        for model_key in spec.in_models_keys:
            try:
                in_tuple = self._db.get(schemas.Type.Traintuple, key=model_key)
                in_models.append(in_tuple.out_model.dict(by_alias=True))
                in_permissions.append(in_tuple.permissions.process)
            except exceptions.NotFound:
                in_tuple = self._db.get(schemas.Type.CompositeTraintuple, key=model_key)
                in_models.append(in_tuple.out_head_model.out_model.dict(by_alias=True))
                in_permissions.append(in_tuple.out_head_model.permissions.process)
            in_tuples.append(in_tuple)

        # Hash key
        key_components = spec.in_models_keys + [spec.algo_key]
        key = hasher.Hasher(values=key_components).compute()

        # Compute plan
        compute_plan_id, rank = self.__create_compute_plan_from_tuple(spec, key, in_tuples)

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
            creator=_BACKEND_ID,
            worker=spec.worker,
            algo_key=spec.algo_key,
            permissions={
                "process": {
                    "authorized_ids": authorized_ids,
                    "public": public
                }
            },
            tag=spec.tag or '',
            compute_plan_id=compute_plan_id,
            rank=rank,
            status=models.Status.waiting,
            log='',
            in_models=in_models,
            out_model=None,
            metadata=spec.metadata or dict()
        )
        aggregatetuple = self._db.add(aggregatetuple, exist_ok)
        if aggregatetuple.status == models.Status.waiting:
            self._worker.schedule_traintuple(aggregatetuple)
        return aggregatetuple

    def _download_algo(self, url_field_path, key, destination):
        asset = self._db.get(type_=schemas.Type.Algo, key=key)
        shutil.copyfile(asset.file, destination)

    def _download_dataset(self, url_field_path, key, destination):
        asset = self._db.get(type_=schemas.Type.Dataset, key=key)
        shutil.copyfile(asset.data_opener, destination)

    def _download_objective(self, url_field_path, key, destination):
        asset = self._db.get(type_=schemas.Type.Objective, key=key)
        shutil.copyfile(asset.metrics, destination)

    def add(self, spec, exist_ok, spec_options=None):
        # find dynamically the method to call to create the asset
        method_name = f"_add_{spec.__class__.type_.value}"
        if spec.is_many():
            method_name += "s"
        add_asset = getattr(self, method_name)
        asset = add_asset(spec, exist_ok, spec_options)
        if spec.is_many():
            return [a.to_response() for a in asset]
        else:
            return asset.to_response()

    def link_dataset_with_objective(self, dataset_key, objective_key):
        # validation
        dataset = self._db.get(schemas.Type.Dataset, dataset_key)
        self._db.get(schemas.Type.Objective, objective_key)
        if dataset.objective_key:
            raise substra.exceptions.InvalidRequest(
                "Dataset already linked to an objective", 400
            )

        dataset.objective_key = objective_key
        return {"pkhash": dataset.key}

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

    def download(self, asset_type, url_field_path, key, destination):
        method_name = f"_download_{asset_type.value}"
        download_asset = getattr(self, method_name)
        download_asset(url_field_path, key, destination)

    def describe(self, asset_type, key):
        asset = self._db.get(type_=asset_type, key=key)
        if not hasattr(asset, "description") or not asset.description:
            raise ValueError("This element does not have a description.")
        with open(asset.description, "r", encoding="utf-8") as f:
            return f.read()

    def leaderboard(self, objective_key, sort='desc'):
        objective = self._db.get(schemas.Type.Objective, objective_key)
        testtuples = self._db.list(schemas.Type.Testtuple)
        certified_testtuples = [
            self.__format_for_leaderboard(t)
            for t in testtuples
            if t.objective_key == objective_key and t.certified
        ]
        certified_testtuples.sort(key=lambda x: x['perf'], reverse=(sort == 'desc'))
        board = {
            'objective': objective.to_response(),
            'testtuples': certified_testtuples
        }
        return board

    def cancel_compute_plan(self, compute_plan_id):
        # Execution is synchronous in the local backend so this
        # function does not make sense.
        raise NotImplementedError

    def update_compute_plan(self, compute_plan_id: str, spec: schemas.UpdateComputePlanSpec):
        compute_plan = self._db.get(schemas.Type.ComputePlan, compute_plan_id)

        # Get all the new tuples and their dependencies
        (
            all_tuples,
            traintuples,
            aggregatetuples,
            compositetuples
        ) = self.__get_all_tuples_compute_plan(spec)

        # Define the rank of each traintuple, aggregate tuple and composite tuple
        old_tuples = {id_: list() for id_ in compute_plan.id_to_key}
        all_tuples.update(old_tuples)

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
                    schemas.Type.Traintuple,
                    key,
                    compute_plan.id_to_key
                )
                visited[id_] = rank

        if compute_plan.composite_traintuple_keys:
            for key in compute_plan.composite_traintuple_keys:
                id_, rank = self.__get_id_rank_in_compute_plan(
                    schemas.Type.Traintuple,
                    key,
                    compute_plan.id_to_key
                )
                visited[id_] = rank

        visited = utils.compute_ranks(node_graph=all_tuples, visited=visited)

        compute_plan = self.__execute_compute_plan(
            spec,
            compute_plan,
            visited,
            traintuples,
            aggregatetuples,
            compositetuples,
            exist_ok=False,
            spec_options=dict()
        )
        return compute_plan.to_response()
