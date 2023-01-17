import abc
import enum
import re
from datetime import datetime
from typing import ClassVar
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Union

import pydantic
from pydantic import AnyUrl
from pydantic import DirectoryPath
from pydantic import FilePath
from pydantic.fields import Field

from substra.sdk import schemas

# The remote can return an URL or an empty string for paths
UriPath = Union[FilePath, AnyUrl, str]
CAMEL_TO_SNAKE_PATTERN = re.compile(r"(.)([A-Z][a-z]+)")
CAMEL_TO_SNAKE_PATTERN_2 = re.compile(r"([a-z0-9])([A-Z])")


class MetadataFilterType(str, enum.Enum):
    is_equal = "is"
    contains = "contains"
    exists = "exists"


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
    empty = "PLAN_STATUS_EMPTY"


class TaskErrorType(str, enum.Enum):
    """Types of errors that can occur in a task"""

    build = "BUILD_ERROR"
    execution = "EXECUTION_ERROR"
    internal = "INTERNAL_ERROR"


class OrderingFields(str, enum.Enum):
    """Model fields ordering is allowed on for list"""

    creation_date = "creation_date"
    start_date = "start_date"
    end_date = "end_date"

    @classmethod
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class Permission(schemas._PydanticConfig):
    """Permissions of a task"""

    public: bool
    authorized_ids: List[str]


class Permissions(schemas._PydanticConfig):
    """Permissions structure stored in various asset types."""

    process: Permission


class _Model(schemas._PydanticConfig, abc.ABC):
    """Asset creation specification base class."""

    # pretty print
    def __str__(self):
        return self.json(indent=4)

    def __repr__(self):
        return self.json(indent=4)

    @staticmethod
    def allowed_filters() -> List[str]:
        """allowed fields to filter on"""
        return list()


class DataSample(_Model):
    """Data sample"""

    key: str
    owner: str
    data_manager_keys: Optional[List[str]]
    path: Optional[DirectoryPath]
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.DataSample

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "owner", "compute_plan_key", "algo_key", "dataset_key"]


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
    data_sample_keys: List[str] = list()
    opener: _File
    description: _File
    metadata: Dict[str, str]
    creation_date: datetime
    logs_permission: Permission

    type_: ClassVar[str] = schemas.Type.Dataset

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "name", "owner", "permissions", "compute_plan_key", "algo_key", "data_sample_key"]


class AlgoInput(_Model):
    identifier: str
    kind: schemas.AssetKind
    optional: bool
    multiple: bool


class AlgoOutput(_Model):
    identifier: str
    kind: schemas.AssetKind
    multiple: bool


class Algo(_Model):
    key: str
    name: str
    owner: str
    permissions: Permissions
    metadata: Dict[str, str]
    creation_date: datetime
    inputs: List[AlgoInput]
    outputs: List[AlgoOutput]

    description: _File
    algorithm: _File

    type_: ClassVar[str] = schemas.Type.Algo

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "name", "owner", "permissions", "compute_plan_key", "dataset_key", "data_sample_key"]

    @pydantic.validator("inputs", pre=True)
    def dict_input_to_list(cls, v):  # noqa: N805
        if isinstance(v, dict):
            # Transform the inputs dict to a list
            return [
                AlgoInput(
                    identifier=identifier,
                    kind=algo_input["kind"],
                    optional=algo_input["optional"],
                    multiple=algo_input["multiple"],
                )
                for identifier, algo_input in v.items()
            ]
        else:
            return v

    @pydantic.validator("outputs", pre=True)
    def dict_output_to_list(cls, v):  # noqa: N805
        if isinstance(v, dict):
            # Transform the outputs dict to a list
            return [
                AlgoOutput(identifier=identifier, kind=algo_output["kind"], multiple=algo_output["multiple"])
                for identifier, algo_output in v.items()
            ]
        else:
            return v


class InModel(schemas._PydanticConfig):
    """In model of a task"""

    checksum: str
    storage_address: UriPath


class OutModel(schemas._PydanticConfig):
    """Out model of a task"""

    key: str
    compute_task_key: str
    address: Optional[InModel]
    permissions: Permissions
    owner: str
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Model

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "compute_task_key", "owner", "permissions"]


class InputRef(schemas._PydanticConfig):
    identifier: str
    asset_key: Optional[str]
    parent_task_key: Optional[str]
    parent_task_output_identifier: Optional[str]

    # either (asset_key) or (parent_task_key, parent_task_output_identifier) must be specified
    _check_asset_key_or_parent_ref = pydantic.root_validator(allow_reuse=True)(schemas.check_asset_key_or_parent_ref)


class ComputeTaskOutput(schemas._PydanticConfig):
    """Specification of a compute task input"""

    permissions: Permissions
    value: Optional[Union[float, OutModel, List[OutModel]]]  # performance or Model or multiple model
    is_transient: bool = Field(False, alias="transient")

    class Config:
        allow_population_by_field_name = True


class Task(_Model):
    key: str
    algo: Algo
    owner: str
    compute_plan_key: str
    metadata: Dict[str, str]
    status: Status
    worker: str
    rank: Optional[int]
    inputs: List[InputRef]
    outputs: Dict[str, ComputeTaskOutput]
    tag: str
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    error_type: Optional[TaskErrorType] = None

    type_: ClassVar[Type] = schemas.Type.Task

    @staticmethod
    def allowed_filters() -> List[str]:
        return [
            "key",
            "owner",
            "worker",
            "rank",
            "status",
            "metadata",
            "compute_plan_key",
            "algo_key",
        ]


Task.update_forward_refs()


class FailedTuple(_Model):
    """Info on failed tuple."""

    key: str
    category: str


class ComputePlan(_Model):
    """ComputePlan"""

    key: str
    tag: str
    name: str
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
    status: ComputePlanStatus
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    estimated_end_date: Optional[datetime]
    duration: Optional[int]
    creator: Optional[str]

    type_: ClassVar[str] = schemas.Type.ComputePlan

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "name", "owner", "worker", "status", "metadata", "algo_key", "dataset_key", "data_sample_key"]


class Performances(_Model):
    """Performances of the different compute tasks of a compute plan"""

    compute_plan_key: List[str] = list()
    compute_plan_tag: List[str] = list()
    compute_plan_status: List[str] = list()
    compute_plan_start_date: List[datetime] = list()
    compute_plan_end_date: List[datetime] = list()
    compute_plan_metadata: List[dict] = list()
    worker: List[str] = list()
    testtuple_key: List[str] = list()
    metric_name: List[str] = list()
    testtuple_rank: List[int] = list()
    round_idx: List[int] = list()
    performance: List[float] = list()


class Organization(schemas._PydanticConfig):
    """Organization"""

    id: str
    is_current: bool
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Organization


class OrganizationInfoConfig(schemas._PydanticConfig):
    model_export_enabled: bool


class OrganizationInfo(schemas._PydanticConfig):
    host: AnyUrl
    organization_id: str
    organization_name: str
    config: OrganizationInfoConfig
    channel: str
    version: str
    orchestrator_version: str


SCHEMA_TO_MODEL = {
    schemas.Type.Task: Task,
    schemas.Type.Algo: Algo,
    schemas.Type.ComputePlan: ComputePlan,
    schemas.Type.DataSample: DataSample,
    schemas.Type.Dataset: Dataset,
    schemas.Type.Organization: Organization,
    schemas.Type.Model: OutModel,
}
