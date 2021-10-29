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

import abc
import contextlib
import enum
import json
import pathlib
import typing
from typing import Optional, List, Dict
import uuid

import pydantic

from substra.sdk import utils

# TODO create a sub-package schemas:
# types
# inputs
# outputs


_SERVER_NAMES = {
    'dataset': 'data_manager',
}


class Type(enum.Enum):
    Algo = 'algo'
    DataSample = 'data_sample'
    Dataset = 'dataset'
    Model = 'model'
    Metric = 'metric'
    Testtuple = 'testtuple'
    Traintuple = 'traintuple'
    Aggregatetuple = 'aggregatetuple'
    CompositeTraintuple = 'composite_traintuple'
    ComputePlan = 'compute_plan'
    Node = 'node'

    def to_server(self):
        """Returns the name used to identify the asset on the backend."""
        name = self.value
        return _SERVER_NAMES.get(name, name)

    def __str__(self):
        return self.name


class AlgoCategory(str, enum.Enum):
    """Algo category"""
    unknown = "ALGO_UNKNOWN"
    simple = "ALGO_SIMPLE"
    composite = "ALGO_COMPOSITE"
    aggregate = "ALGO_AGGREGATE"


class _PydanticConfig(pydantic.BaseModel):
    """Shared configuration for all schemas here"""
    class Config:
        # Ignore extra fields, leave them unexposed
        extra = 'ignore'


class _Spec(_PydanticConfig, abc.ABC):
    """Asset creation specification base class."""

    # pretty print
    def __str__(self):
        return self.json(indent=4)

    def __repr__(self):
        return self.json(indent=4)

    class Meta:
        file_attributes = None

    def is_many(self):
        return False

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # TODO should be located in the backends/remote module
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.json(exclude_unset=True))
        if self.Meta.file_attributes:
            with utils.extract_files(data, self.Meta.file_attributes) as (data, files):
                yield (data, files)
        else:
            yield data, None

    @staticmethod
    def compute_key() -> str:
        return uuid.uuid4().hex


class Permissions(_PydanticConfig):
    """Specification for permissions. If public is False,
    give the list of authorized ids.
    """
    public: bool
    authorized_ids: typing.List[str]  # List of authorized node ids if private


class PrivatePermissions(_PydanticConfig):
    """Specification for private permissions. Only the nodes whose
    ids are in authorized_ids can access the asset.
    """
    authorized_ids: typing.List[str]  # List of authorized node ids


class DataSampleSpec(_Spec):
    """Specification to create one or many data samples
    To create one data sample, use the 'path' field, otherwise use
    the 'paths' field.
    """
    path: Optional[pathlib.Path]  # Path to the data sample if only one
    paths: Optional[List[pathlib.Path]]  # Path to the data samples if several
    test_only: bool  # If the data sample is for train or test
    data_manager_keys: typing.List[str]

    type_: typing.ClassVar[Type] = Type.DataSample

    def is_many(self):
        return self.paths and len(self.paths) > 0

    @pydantic.root_validator(pre=True)
    def exclusive_paths(cls, values):
        """Check that one and only one path(s) field is defined."""
        if 'paths' in values and 'path' in values:
            raise ValueError("'path' and 'paths' fields are exclusive.")
        if 'paths' not in values and 'path' not in values:
            raise ValueError("'path' or 'paths' field must be set.")
        return values

    @contextlib.contextmanager
    def build_request_kwargs(self, local):
        # redefine kwargs builder to handle the local paths
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.json(exclude_unset=True))
        if local:
            with utils.extract_data_sample_files(data) as (data, files):
                yield (data, files)
        else:
            yield data, None


class ComputePlanTraintupleSpec(_Spec):
    """Specification of a traintuple inside a compute
    plan specification"""
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    traintuple_id: str
    in_models_ids: Optional[List[str]]
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]


class ComputePlanAggregatetupleSpec(_Spec):
    """Specification of an aggregate tuple inside a compute
    plan specification"""
    aggregatetuple_id: str
    algo_key: str
    worker: str
    in_models_ids: Optional[List[str]]
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]


class ComputePlanCompositeTraintupleSpec(_Spec):
    """Specification of a composite traintuple inside a compute
    plan specification"""
    composite_traintuple_id: str
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_head_model_id: Optional[str]
    in_trunk_model_id: Optional[str]
    tag: Optional[str]
    out_trunk_model_permissions: Permissions
    metadata: Optional[Dict[str, str]]


class ComputePlanTesttupleSpec(_Spec):
    """Specification of a testtuple inside a compute
    plan specification"""
    metric_keys: List[str]
    traintuple_id: str
    tag: Optional[str]
    data_manager_key: str
    test_data_sample_keys: List[str]
    metadata: Optional[Dict[str, str]]


class _BaseComputePlanSpec(_Spec, abc.ABC):
    traintuples: Optional[List[ComputePlanTraintupleSpec]]
    composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
    aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
    testtuples: Optional[List[ComputePlanTesttupleSpec]]


class ComputePlanSpec(_BaseComputePlanSpec):
    """Specification for creating a compute plan"""
    tag: Optional[str]
    clean_models: Optional[bool]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.ComputePlan


class UpdateComputePlanSpec(_BaseComputePlanSpec):
    """Specification for updating a compute plan"""
    pass


class DatasetSpec(_Spec):
    """Specification for creating a dataset"""
    name: str
    data_opener: pathlib.Path  # Path to the data opener
    type: str
    description: pathlib.Path  # Path to the description file
    permissions: Permissions
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Dataset

    class Meta:
        file_attributes = ('data_opener', 'description', )


class MetricSpec(_Spec):
    """Specification for creating an metric"""
    name: str
    description: pathlib.Path  # Path to the description file
    file: pathlib.Path  # Path to the metrics file
    permissions: Permissions
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Metric

    class Meta:
        file_attributes = ('file', 'description', )


class AlgoSpec(_Spec):
    """Specification for creating an algo"""
    name: str
    description: pathlib.Path
    file: pathlib.Path
    permissions: Permissions
    metadata: Optional[Dict[str, str]]
    category: AlgoCategory

    type_: typing.ClassVar[Type] = Type.Algo

    class Meta:
        file_attributes = ('file', 'description', )


class TraintupleSpec(_Spec):
    """Specification for creating a traintuple"""
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_models_keys: Optional[List[str]]
    tag: Optional[str]
    compute_plan_key: Optional[str]
    rank: Optional[int]  # Rank of the traintuple in the compute plan
    metadata: Optional[Dict[str, str]]

    compute_plan_attr_name: typing.ClassVar[str] = "traintuple_keys"
    type_: typing.ClassVar[Type] = Type.Traintuple

    @classmethod
    def from_compute_plan(
        cls,
        compute_plan_key: str,
        rank: int,
        spec: ComputePlanTraintupleSpec
    ) -> "TraintupleSpec":
        return TraintupleSpec(
            algo_key=spec.algo_key,
            data_manager_key=spec.data_manager_key,
            train_data_sample_keys=spec.train_data_sample_keys,
            in_models_keys=spec.in_models_ids or list(),
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata
        )


class AggregatetupleSpec(_Spec):
    """Specification for creating an aggregate tuple"""
    algo_key: str
    worker: str
    in_models_keys: List[str]
    tag: Optional[str]
    compute_plan_key: Optional[str]
    rank: Optional[int]
    metadata: Optional[Dict[str, str]]

    compute_plan_attr_name: typing.ClassVar[str] = "aggregatetuple_keys"
    type_: typing.ClassVar[Type] = Type.Aggregatetuple

    @classmethod
    def from_compute_plan(
        cls,
        compute_plan_key: str,
        rank: int,
        spec: ComputePlanAggregatetupleSpec
    ) -> "AggregatetupleSpec":
        return AggregatetupleSpec(
            algo_key=spec.algo_key,
            worker=spec.worker,
            in_models_keys=spec.in_models_ids or list(),
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata
        )


class CompositeTraintupleSpec(_Spec):
    """Specification for creating a composite traintuple"""
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_head_model_key: Optional[str]
    in_trunk_model_key: Optional[str]
    tag: Optional[str]
    compute_plan_key: Optional[str]
    out_trunk_model_permissions: Permissions
    rank: Optional[int]
    metadata: Optional[Dict[str, str]]

    compute_plan_attr_name: typing.ClassVar[str] = "composite_traintuple_keys"
    type_: typing.ClassVar[Type] = Type.CompositeTraintuple

    @classmethod
    def from_compute_plan(
        cls,
        compute_plan_key: str,
        rank: int,
        spec: ComputePlanCompositeTraintupleSpec
    ) -> "CompositeTraintupleSpec":
        return CompositeTraintupleSpec(
            algo_key=spec.algo_key,
            data_manager_key=spec.data_manager_key,
            train_data_sample_keys=spec.train_data_sample_keys,
            in_head_model_key=spec.in_head_model_id,
            in_trunk_model_key=spec.in_trunk_model_id,
            out_trunk_model_permissions={
                "public": spec.out_trunk_model_permissions.public,
                "authorized_ids": spec.out_trunk_model_permissions.authorized_ids
            },
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata
        )


class TesttupleSpec(_Spec):
    """Specification for creating a testtuple"""
    metric_keys: List[str]
    traintuple_key: str
    tag: Optional[str]
    data_manager_key: str
    test_data_sample_keys: List[str]
    compute_plan_key: Optional[str]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Testtuple

    @classmethod
    def from_compute_plan(
        cls,
        spec: ComputePlanTesttupleSpec
    ) -> "TesttupleSpec":
        return TesttupleSpec(
            metric_keys=spec.metric_keys,
            traintuple_key=spec.traintuple_id,
            tag=spec.tag,
            data_manager_key=spec.data_manager_key,
            test_data_sample_keys=spec.test_data_sample_keys,
            metadata=spec.metadata,
        )
