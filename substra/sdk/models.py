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
import enum
import re

from typing import ClassVar, Dict, List, Optional, Union

from pydantic import DirectoryPath, FilePath, AnyUrl

from substra.sdk import schemas

# The remote can return an URL or an empty string for paths
UriPath = Union[FilePath, AnyUrl, str]
CAMEL_TO_SNAKE_PATTERN = re.compile(r'(.)([A-Z][a-z]+)')
CAMEL_TO_SNAKE_PATTERN_2 = re.compile(r'([a-z0-9])([A-Z])')


def _to_snake_case(camel_str):
    name = CAMEL_TO_SNAKE_PATTERN.sub(r'\1_\2', camel_str)
    name = CAMEL_TO_SNAKE_PATTERN_2.sub(r'\1_\2', name).lower()
    return name.replace('_i_d', '_id')


class Status(str, enum.Enum):
    """Status of the task"""
    doing = "doing"
    done = "done"
    failed = "failed"
    todo = "todo"
    waiting = "waiting"
    canceled = "canceled"


class Permission(schemas._PydanticConfig):
    """Permissions of a task"""
    public: bool
    authorized_ids: List[str]


class Permissions(schemas._PydanticConfig):
    """Permissions structure stored in various asset types."""
    process: Permission
    download: Permission


class _Model(schemas._PydanticConfig, abc.ABC):
    """Asset creation specification base class."""

    def __str__(self):
        return f"{self.__class__.type_.value}(key={self.key})"


class DataSample(_Model):
    """Data sample"""
    key: str
    owner: str
    data_manager_keys: Optional[List[str]]
    path: Optional[DirectoryPath]
    validated: bool = True
    # The backend does not return this but it is needed for link_dataset_with_data_samples
    test_only: bool = False

    type_: ClassVar[str] = schemas.Type.DataSample


class _File(schemas._PydanticConfig):
    """File as stored in the models"""
    checksum: str
    storage_address: UriPath


class Dataset(_Model):
    """Dataset asset"""
    key: str
    name: str
    owner: str
    objective_key: Optional[str]
    permissions: Permissions
    type: str
    train_data_sample_keys: List[str] = list()
    test_data_sample_keys: List[str] = list()
    opener: _File
    description: _File
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.Dataset


# class _ObjectiveDataset(schemas._PydanticConfig):
#     """Dataset as stored in the Objective asset"""
#     data_manager_key: str
#     data_sample_keys: List[str]
#     metadata: Dict[str, str]
#     worker: str


class _Metric(schemas._PydanticConfig):
    """Metric associated to a testtuple or objective"""
    checksum: str
    storage_address: UriPath


class Objective(_Model):
    """Objective"""
    key: str
    name: str
    owner: str
    data_manager_key: str
    data_sample_keys: List[str]
    # test_dataset: Optional[_ObjectiveDataset]
    metadata: Dict[str, str]
    permissions: Permissions

    description: _File
    metrics_name: Optional[str]
    metrics: _Metric

    type_: ClassVar[str] = schemas.Type.Objective


class _Algo(_Model):
    key: str
    name: str
    owner: str
    permissions: Permissions
    metadata: Dict[str, str]
    category: str

    description: _File
    algorithm: _File


class Algo(_Algo):
    """Algo"""
    type_: ClassVar[str] = schemas.Type.Algo


class AggregateAlgo(_Algo):
    """AggregateAlgo"""
    type_: ClassVar[str] = schemas.Type.AggregateAlgo


class CompositeAlgo(_Algo):
    """CompositeAlgo"""
    type_: ClassVar[str] = schemas.Type.CompositeAlgo


# class _TraintupleDataset(schemas._PydanticConfig):
#     """Dataset as stored in a traintuple or composite traintuple"""
#     key: str
#     opener_checksum: str
#     data_sample_keys: List[str]
#     worker: str
#     metadata: Optional[Dict[str, str]]


class InModel(schemas._PydanticConfig):
    """In model of a traintuple, aggregate tuple or in trunk
    model of a composite traintuple"""
    key: str
    checksum: str
    storage_address: UriPath
    traintuple_key: Optional[str]


class OutModel(schemas._PydanticConfig):
    """Out model of a traintuple, aggregate tuple or out trunk
    model of a composite traintuple"""
    key: str
    checksum: str
    storage_address: UriPath

    type_: ClassVar[str] = schemas.Type.Model


class _GenericTraintuple(_Model):
    key: str
    category: str
    algo: Algo
    owner: str
    compute_plan_key: str
    metadata: Dict[str, str]
    status: str
    worker: str
    rank: Optional[int]
    parent_task_keys: List[str]


class _Composite(schemas._PydanticConfig):
    data_manager_key: str
    data_sample_keys: List[str]
    head_permissions: Permissions
    trunk_permissions: Permissions


class _Train(schemas._PydanticConfig):
    data_manager_key: str
    data_sample_keys: List[str]
    model_permissions: Permissions


class _Aggregate(schemas._PydanticConfig):
    model_permissions: Permissions


class _Test(schemas._PydanticConfig):
    data_manager_key: str
    data_sample_keys: List[str]
    objective_key: str
    certified: bool


class Traintuple(_GenericTraintuple):
    """Traintuple"""
    train: _Train


class Aggregatetuple(_GenericTraintuple):
    """Aggregatetuple"""
    aggregate: _Aggregate


class CompositeTraintuple(_GenericTraintuple):
    """CompositeTraintuple"""
    composite: _Composite


class Testtuple(_GenericTraintuple):
    """Testtuple"""
    test: _Test

    # @pydantic.validator('traintuple_type', pre=True)
    # def traintuple_type_snake_case(cls, v):
    #     return _to_snake_case(v)


class FailedTuple(_Model):
    """Info on failed tuple."""
    key: str
    type: str


class ComputePlan(_Model):
    """ComputePlan"""
    key: str
    tag: str
    owner: str
    metadata: Dict[str, str]
    done_count: int
    task_count: int
    delete_intermediary_models: bool = False

    # status: str
    # failed_tuple: FailedTuple
    # traintuple_keys: Optional[List[str]]
    # composite_traintuple_keys: Optional[List[str]]
    # aggregatetuple_keys: Optional[List[str]]
    # testtuple_keys: Optional[List[str]]
    # id_to_key: Dict[str, str]

    def __str__(self):
        return f"{self.__class__.type_.value}(key={self.key})"


class Node(schemas._PydanticConfig):
    """Node"""
    id: str
    is_current: bool


SCHEMA_TO_MODEL = {
    schemas.Type.AggregateAlgo: AggregateAlgo,
    schemas.Type.Aggregatetuple: Aggregatetuple,
    schemas.Type.Algo: Algo,
    schemas.Type.CompositeAlgo: CompositeAlgo,
    schemas.Type.CompositeTraintuple: CompositeTraintuple,
    schemas.Type.ComputePlan: ComputePlan,
    schemas.Type.DataSample: DataSample,
    schemas.Type.Dataset: Dataset,
    schemas.Type.Objective: Objective,
    schemas.Type.Testtuple: Testtuple,
    schemas.Type.Traintuple: Traintuple,
    schemas.Type.Node: Node
}
