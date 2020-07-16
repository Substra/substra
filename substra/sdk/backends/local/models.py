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
import json
from typing import ClassVar, Dict, List, Optional

import pydantic
from pydantic import DirectoryPath, FilePath

from substra.sdk import schemas


def _to_camel_case(snake_str):
    """Convert a snake case string to a camel case string."""
    components = snake_str.split("_")
    # we capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


def _replace_dict_keys(d, converter):
    """Replace fields in a dict and return updated dict (recursive).

    Apply converter to each dict field.
    """
    assert isinstance(d, dict)
    new_d = {}
    for key, value in d.items():
        if isinstance(value, dict):
            value = _replace_dict_keys(value, converter)
        elif isinstance(value, list):
            if all([isinstance(v, dict) for v in value]):
                value = [_replace_dict_keys(v, converter) for v in value]

        new_d[converter(key)] = value
    return new_d


class Status(enum.Enum):
    doing = "doing"
    done = "done"
    failed = "failed"
    todo = "todo"
    waiting = "waiting"
    canceled = "canceled"


class Permission(pydantic.BaseModel):
    public: bool
    authorized_ids: List[str]

    class Config:
        extra = 'forbid'


class Permissions(pydantic.BaseModel):
    """Permissions structure stored in various asset types."""

    process: Permission

    class Config:
        extra = 'forbid'


class _Model(pydantic.BaseModel, abc.ABC):
    """Asset creation specification base class."""

    class Meta:
        storage_only_fields = None
        alias_fields = None

    class Config:
        extra = 'forbid'

    def to_response(self):
        """Convert model to backend response object."""
        # serialize and deserialzie to JSON to ensure all field types are converted
        # to JSON compatible formats (this is necessary to handle properly the FilePath
        # fields for isntance).
        data = json.loads(self.json(exclude_none=False))
        if self.__class__.Meta.storage_only_fields:
            for field in self.__class__.Meta.storage_only_fields:
                data.pop(field)

        if self.__class__.Meta.alias_fields:
            for field, field_response in self.__class__.Meta.alias_fields.items():
                value = data.pop(field)
                data[field_response] = value

        # convert snake case to camel case fields
        return _replace_dict_keys(data, _to_camel_case)

    def __str__(self):
        return f"{self.__class__.type_.value}(key={self.key})"


class DataSample(_Model):
    key: str
    pkhash: str
    owner: str
    data_manager_keys: List[str]
    path: DirectoryPath
    validated: bool = True
    test_only: bool

    type_: ClassVar[str] = schemas.Type.DataSample


class Dataset(_Model):
    key: str
    pkhash: str
    name: str
    owner: str
    objective_key: Optional[str]
    permissions: Permissions
    type: str
    train_data_sample_keys: List[str]
    test_data_sample_keys: List[str]
    data_opener: FilePath
    description: FilePath
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.Dataset

    class Meta:
        storage_only_fields = ("data_opener",)
        alias_fields = None


class _ObjectiveDataset(pydantic.BaseModel):
    dataset_key: str
    data_sample_keys: List[str]


class Objective(_Model):
    key: str
    pkhash: str
    name: str
    owner: str
    test_dataset: Optional[_ObjectiveDataset]
    metadata: Dict[str, str]
    permissions: Permissions

    description: FilePath
    metrics: FilePath

    type_: ClassVar[str] = schemas.Type.Objective

    class Meta:
        storage_only_fields = None
        alias_fields = None


class _Algo(_Model):
    key: str
    pkhash: str
    name: str
    owner: str
    permissions: Permissions
    metadata: Dict[str, str]

    description: FilePath
    file: FilePath

    class Meta:
        storage_only_fields = ("file",)
        alias_fields = None


class Algo(_Algo):
    type_: ClassVar[str] = schemas.Type.Algo


class AggregateAlgo(_Algo):
    type_: ClassVar[str] = schemas.Type.AggregateAlgo


class CompositeAlgo(_Algo):
    type_: ClassVar[str] = schemas.Type.CompositeAlgo


class _TraintupleDataset(pydantic.BaseModel):
    opener_hash: str
    keys: List[str]
    worker: str

    @property
    def key(self):
        return self.opener_hash


class InModel(pydantic.BaseModel):
    hash_: str = pydantic.Field(..., alias="hash")
    storage_address: FilePath

    @property
    def key(self):
        return self.hash_


class OutModel(pydantic.BaseModel):
    hash_: str = pydantic.Field(..., alias="hash")
    storage_address: FilePath

    @property
    def key(self):
        return self.hash_


class Traintuple(_Model):
    key: str
    creator: str
    worker: str
    algo_key: str
    dataset: _TraintupleDataset
    permissions: Permissions
    tag: str
    compute_plan_id: str
    rank: int
    status: Status
    log: str
    in_models: List[InModel]
    out_model: Optional[OutModel]
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.Traintuple
    algo_type: ClassVar[schemas.Type] = schemas.Type.Algo

    class Meta:
        storage_only_fields = None
        alias_fields = {"compute_plan_id": "compute_plan_i_d"}


class Aggregatetuple(_Model):
    key: str
    creator: str
    worker: str
    algo_key: str
    permissions: Permissions
    tag: str
    compute_plan_id: str
    rank: Optional[int]
    status: Status
    log: str
    in_models: List[InModel]
    out_model: Optional[OutModel]
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.Aggregatetuple
    algo_type: ClassVar[schemas.Type] = schemas.Type.AggregateAlgo

    class Meta:
        storage_only_fields = None
        alias_fields = {"compute_plan_id": "compute_plan_i_d"}


class OutCompositeModel(pydantic.BaseModel):
    permissions: Permissions
    out_model: Optional[OutModel]


class CompositeTraintuple(_Model):
    key: str
    creator: str
    worker: str
    algo_key: str
    dataset: _TraintupleDataset
    tag: str
    compute_plan_id: str
    rank: Optional[int]
    status: Status
    log: str
    in_head_model: Optional[InModel]
    in_trunk_model: Optional[InModel]
    # This is different from the remote backend
    # We store the out head model storage address directly in the object
    out_head_model: OutCompositeModel
    out_trunk_model: OutCompositeModel
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.CompositeTraintuple
    algo_type: ClassVar[schemas.Type] = schemas.Type.CompositeAlgo

    class Meta:
        storage_only_fields = None
        alias_fields = {"compute_plan_id": "compute_plan_i_d"}


class _TesttupleDataset(pydantic.BaseModel):
    opener_hash: str
    perf: float
    keys: List[str]
    worker: str

    @property
    def key(self):
        return self.opener_hash


class Testtuple(_Model):
    key: str
    creator: str
    objective_key: str
    traintuple_key: str
    certified: bool
    dataset: _TesttupleDataset
    tag: Optional[str]
    log: str
    status: Status
    compute_plan_id: str
    rank: int
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.Testtuple

    class Meta:
        storage_only_fields = None
        alias_fields = {"compute_plan_id": "compute_plan_i_d"}


class ComputePlan(_Model):
    compute_plan_id: str
    status: Status
    traintuple_keys: Optional[List[str]]
    composite_traintuple_keys: Optional[List[str]]
    aggregatetuple_keys: Optional[List[str]]
    testtuple_keys: Optional[List[str]]
    id_to_key: Dict[str, str]
    tag: str
    tuple_count: int
    done_count: int
    metadata: Dict[str, str]

    type_: ClassVar[str] = schemas.Type.ComputePlan

    class Meta:
        storage_only_fields = None
        alias_fields = {"compute_plan_id": "compute_plan_i_d"}
