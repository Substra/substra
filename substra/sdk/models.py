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
from datetime import datetime
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from pydantic import AnyUrl
from pydantic import DirectoryPath
from pydantic import FilePath
from pydantic import root_validator

from substra.sdk import schemas

# The remote can return an URL or an empty string for paths
UriPath = Union[FilePath, AnyUrl, str]
CAMEL_TO_SNAKE_PATTERN = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_PATTERN_2 = re.compile(r"([a-z0-9])([A-Z])")


def _to_snake_case(camel_str):
    name = CAMEL_TO_SNAKE_PATTERN.sub(r"\1_\2", camel_str)
    name = CAMEL_TO_SNAKE_PATTERN_2.sub(r"\1_\2", name).lower()
    return name.replace("_i_d", "_id")


class Status(str, enum.Enum):
    """Status of the task"""

    unknown = "STATUS_UNKNOWN"
    doing = "STATUS_DOING"
    done = "STATUS_DONE"
    failed = "STATUS_FAILED"
    todo = "STATUS_TODO"
    waiting = "STATUS_WAITING"
    canceled = "STATUS_CANCELED"


class ComputePlanStatus(str, enum.Enum):
    """Status of the compute plan"""

    unknown = "PLAN_STATUS_UNKNOWN"
    doing = "PLAN_STATUS_DOING"
    done = "PLAN_STATUS_DONE"
    failed = "PLAN_STATUS_FAILED"
    todo = "PLAN_STATUS_TODO"
    waiting = "PLAN_STATUS_WAITING"
    canceled = "PLAN_STATUS_CANCELED"


class ModelType(str, enum.Enum):
    """Model type"""

    unknown = "MODEL_UNKNOWN"
    head = "MODEL_HEAD"
    simple = "MODEL_SIMPLE"


class TaskCategory(str, enum.Enum):
    """Task category"""

    unknown = "TASK_UNKNOWN"
    train = "TASK_TRAIN"
    aggregate = "TASK_AGGREGATE"
    composite = "TASK_COMPOSITE"
    test = "TASK_TEST"


class Permission(schemas._PydanticConfig):
    """Permissions of a task"""

    public: bool
    authorized_ids: List[str]


class Permissions(schemas._PydanticConfig):
    """Permissions structure stored in various asset types."""

    process: Permission
    download: Permission

    @root_validator(pre=True)
    def set_process(cls, values):
        if "download" not in values:
            values["download"] = values["process"]
        return values


class _Model(schemas._PydanticConfig, abc.ABC):
    """Asset creation specification base class."""

    # pretty print
    def __str__(self):
        return self.json(indent=4)

    def __repr__(self):
        return self.json(indent=4)


class DataSample(_Model):
    """Data sample"""

    key: str
    owner: str
    data_manager_keys: Optional[List[str]]
    path: Optional[DirectoryPath]
    validated: bool = True
    creation_date: datetime
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
    permissions: Permissions
    type: str
    train_data_sample_keys: List[str] = list()
    test_data_sample_keys: List[str] = list()
    opener: _File
    description: _File
    metadata: Dict[str, str]
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Dataset


class _Metric(schemas._PydanticConfig):
    """Metric associated to a testtuple or metric"""

    checksum: str
    storage_address: UriPath


class Metric(_Model):
    """Metric"""

    key: str
    name: str
    owner: str
    metadata: Dict[str, str]
    permissions: Permissions
    creation_date: datetime

    description: _File
    address: _Metric

    type_: ClassVar[str] = schemas.Type.Metric


class Algo(_Model):
    key: str
    name: str
    owner: str
    permissions: Permissions
    metadata: Dict[str, str]
    category: schemas.AlgoCategory
    creation_date: datetime

    description: _File
    algorithm: _File

    type_: ClassVar[str] = schemas.Type.Algo


class InModel(schemas._PydanticConfig):
    """In model of a traintuple, aggregate or composite traintuple"""

    checksum: str
    storage_address: UriPath


class OutModel(schemas._PydanticConfig):
    """Out model of a traintuple, aggregate tuple or out trunk
    model of a composite traintuple"""

    key: str
    category: ModelType
    compute_task_key: str
    address: Optional[InModel]
    permissions: Permissions
    owner: str
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Model


class _GenericTraintuple(_Model):
    key: str
    category: TaskCategory
    algo: Algo
    owner: str
    compute_plan_key: str
    metadata: Dict[str, str]
    status: str
    worker: str
    rank: Optional[int]
    parent_task_keys: List[str]
    parent_tasks: Optional[List[Union["Traintuple", "CompositeTraintuple", "Aggregatetuple"]]] = list()
    tag: str
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]


def check_data_manager_key(cls, values):
    if values.get("data_manager"):
        assert values["data_manager_key"] == values["data_manager"].key, "data_manager does not match data_manager_key"
    return values


class _Composite(schemas._PydanticConfig):
    data_manager_key: str
    data_manager: Optional[Dataset] = None
    data_sample_keys: List[str]
    head_permissions: Permissions
    trunk_permissions: Permissions
    models: Optional[List[OutModel]]

    _check_data_manager_key = root_validator(allow_reuse=True)(check_data_manager_key)


class _Train(schemas._PydanticConfig):
    data_manager_key: str
    data_manager: Optional[Dataset] = None
    data_sample_keys: List[str]
    model_permissions: Permissions
    models: Optional[List[OutModel]]

    _check_data_manager_key = root_validator(allow_reuse=True)(check_data_manager_key)


class _Aggregate(schemas._PydanticConfig):
    model_permissions: Permissions
    models: Optional[List[OutModel]]


class _Test(schemas._PydanticConfig):
    data_manager_key: str
    data_manager: Optional[Dataset] = None
    data_sample_keys: List[str]
    metric_keys: List[str]
    metrics: Optional[List[Metric]] = list()
    perfs: Optional[Dict[str, float]]

    _check_data_manager_key = root_validator(allow_reuse=True)(check_data_manager_key)

    @root_validator
    def check_metric_keys(cls, values):
        if values.get("metrics"):
            assert values["metric_keys"] == [m.key for m in values["metrics"]], "metrics do not match metric_keys"
        return values


class Traintuple(_GenericTraintuple):
    """Traintuple"""

    train: _Train
    type_: ClassVar[str] = schemas.Type.Traintuple


class Aggregatetuple(_GenericTraintuple):
    """Aggregatetuple"""

    aggregate: _Aggregate
    type_: ClassVar[str] = schemas.Type.Aggregatetuple


class CompositeTraintuple(_GenericTraintuple):
    """CompositeTraintuple"""

    composite: _Composite
    type_: ClassVar[str] = schemas.Type.CompositeTraintuple


_GenericTraintuple.update_forward_refs()
Traintuple.update_forward_refs()
Aggregatetuple.update_forward_refs()
CompositeTraintuple.update_forward_refs()


class Testtuple(_GenericTraintuple):
    """Testtuple"""

    test: _Test
    type_: ClassVar[str] = schemas.Type.Testtuple


class FailedTuple(_Model):
    """Info on failed tuple."""

    key: str
    category: str


class ComputePlan(_Model):
    """ComputePlan"""

    key: str
    tag: str
    owner: str
    metadata: Dict[str, str]
    task_count: int = 0
    waiting_count: int = 0
    todo_count: int = 0
    doing_count: int = 0
    canceled_count: int = 0
    failed_count: int = 0
    done_count: int = 0
    failed_task: Optional[FailedTuple]
    delete_intermediary_models: bool = False
    status: ComputePlanStatus
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    estimated_end_date: Optional[datetime]
    duration: Optional[int]

    type_: ClassVar[str] = schemas.Type.ComputePlan


class Node(schemas._PydanticConfig):
    """Node"""

    id: str
    is_current: bool
    creation_date: datetime


SCHEMA_TO_MODEL = {
    schemas.Type.Aggregatetuple: Aggregatetuple,
    schemas.Type.Algo: Algo,
    schemas.Type.CompositeTraintuple: CompositeTraintuple,
    schemas.Type.ComputePlan: ComputePlan,
    schemas.Type.DataSample: DataSample,
    schemas.Type.Dataset: Dataset,
    schemas.Type.Metric: Metric,
    schemas.Type.Testtuple: Testtuple,
    schemas.Type.Traintuple: Traintuple,
    schemas.Type.Node: Node,
    schemas.Type.Model: OutModel,
}
