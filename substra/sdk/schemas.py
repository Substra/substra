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
import pathlib
import typing
from typing import Optional, List, Dict, Union

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
    AggregateAlgo = 'aggregate_algo'
    CompositeAlgo = 'composite_algo'
    DataSample = 'data_sample'
    Dataset = 'dataset'
    Model = 'model'
    Objective = 'objective'
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


class _Spec(pydantic.BaseModel, abc.ABC):
    """Asset creation specification base class."""

    class Meta:
        file_attributes = None

    class Config:
        extra = 'forbid'

    def is_many(self):
        return False

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # TODO should be located in the backends/remote module
        data = self.dict(exclude_unset=True)
        if self.Meta.file_attributes:
            with utils.extract_files(data, self.Meta.file_attributes) as (data, files):
                yield (data, files)
        else:
            yield data, None


class Permissions(pydantic.BaseModel):
    public: bool
    authorized_ids: typing.List[str]

    class Config:
        extra = 'forbid'


class PrivatePermissions(pydantic.BaseModel):
    authorized_ids: typing.List[str]

    class Config:
        extra = 'forbid'


class DataSampleSpec(_Spec):
    path: Optional[Union[str, pathlib.Path]]
    paths: Optional[List[Union[str, pathlib.Path]]]
    test_only: bool
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
        data = self.dict(exclude_unset=True)
        if local:
            with utils.extract_data_sample_files(data) as (data, files):
                yield (data, files)
        else:
            yield data, None


class DatasetSpec(_Spec):
    name: str
    data_opener: Union[str, pathlib.Path]
    type: str
    description: Union[str, pathlib.Path]
    permissions: Permissions
    objective_key: Optional[str]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Dataset

    class Meta:
        file_attributes = ('data_opener', 'description', )


class ObjectiveSpec(_Spec):
    name: str
    description: Union[str, pathlib.Path]
    metrics_name: str
    metrics: Union[str, pathlib.Path]
    test_data_sample_keys: Optional[List[str]]
    test_data_manager_key: Optional[str]
    permissions: Permissions
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Objective

    class Meta:
        file_attributes = ('metrics', 'description', )


class _AlgoSpec(_Spec):
    name: str
    description: Union[str, pathlib.Path]
    file: Union[str, pathlib.Path]
    permissions: Permissions
    metadata: Optional[Dict[str, str]]

    class Meta:
        file_attributes = ('file', 'description', )


class AlgoSpec(_AlgoSpec):
    type_: typing.ClassVar[Type] = Type.Algo


class AggregateAlgoSpec(_AlgoSpec):
    type_: typing.ClassVar[Type] = Type.AggregateAlgo


class CompositeAlgoSpec(_AlgoSpec):
    type_: typing.ClassVar[Type] = Type.CompositeAlgo


class TraintupleSpec(_Spec):
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_models_keys: Optional[List[str]]
    tag: Optional[str]
    compute_plan_id: Optional[str]
    rank: Optional[int]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Traintuple


class AggregatetupleSpec(_Spec):
    algo_key: str
    worker: str
    in_models_keys: List[str]
    tag: Optional[str]
    compute_plan_id: Optional[str]
    rank: Optional[int]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Aggregatetuple


class CompositeTraintupleSpec(_Spec):
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_head_model_key: Optional[str]
    in_trunk_model_key: Optional[str]
    tag: Optional[str]
    compute_plan_id: Optional[str]
    out_trunk_model_permissions: PrivatePermissions
    rank: Optional[int]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.CompositeTraintuple


class TesttupleSpec(_Spec):
    objective_key: str
    traintuple_key: str
    tag: Optional[str]
    data_manager_key: Optional[str]
    test_data_sample_keys: Optional[List[str]]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.Testtuple


class ComputePlanTraintupleSpec(_Spec):
    algo_key: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    traintuple_id: str
    in_models_ids: Optional[List[str]]
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]


class ComputePlanAggregatetupleSpec(_Spec):
    aggregatetuple_id: str
    algo_key: str
    worker: str
    in_models_ids: Optional[List[str]]
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]


class ComputePlanCompositeTraintupleSpec(_Spec):
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
    objective_key: str
    traintuple_id: str
    tag: Optional[str]
    data_manager_key: Optional[str]
    test_data_sample_keys: Optional[List[str]]
    metadata: Optional[Dict[str, str]]


class _BaseComputePlanSpec(_Spec, abc.ABC):
    traintuples: Optional[List[ComputePlanTraintupleSpec]]
    composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
    aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
    testtuples: Optional[List[ComputePlanTesttupleSpec]]


class ComputePlanSpec(_BaseComputePlanSpec):
    tag: Optional[str]
    clean_models: Optional[bool]
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.ComputePlan


class UpdateComputePlanSpec(_BaseComputePlanSpec):
    pass
