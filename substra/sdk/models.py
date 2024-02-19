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
from pydantic import ConfigDict
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


class ComputeTaskStatus(str, enum.Enum):
    """Status of the task"""

    unknown = "STATUS_UNKNOWN"
    building = "STATUS_BUILDING"
    executing = "STATUS_EXECUTING"
    done = "STATUS_DONE"
    failed = "STATUS_FAILED"
    waiting_for_executor_slot = "STATUS_WAITING_FOR_EXECUTOR_SLOT"
    waiting_for_parent_tasks = "STATUS_WAITING_FOR_PARENT_TASKS"
    waiting_for_builder_slot = "STATUS_WAITING_FOR_BUILDER_SLOT"
    canceled = "STATUS_CANCELED"


class ComputePlanStatus(str, enum.Enum):
    """Status of the compute plan"""

    unknown = "PLAN_STATUS_UNKNOWN"
    doing = "PLAN_STATUS_DOING"
    done = "PLAN_STATUS_DONE"
    failed = "PLAN_STATUS_FAILED"
    created = "PLAN_STATUS_CREATED"
    canceled = "PLAN_STATUS_CANCELED"


class FunctionStatus(str, enum.Enum):
    """Status of the function"""

    unknown = "FUNCTION_STATUS_UNKNOWN"
    waiting = "FUNCTION_STATUS_WAITING"
    building = "FUNCTION_STATUS_BUILDING"
    ready = "FUNCTION_STATUS_READY"
    failed = "FUNCTION_STATUS_FAILED"
    canceled = "FUNCTION_STATUS_CANCELED"


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
        return self.model_dump_json(indent=4)

    def __repr__(self):
        return self.model_dump_json(indent=4)

    @staticmethod
    def allowed_filters() -> List[str]:
        """allowed fields to filter on"""
        return []


class DataSample(_Model):
    """Data sample"""

    key: str
    owner: str
    data_manager_keys: Optional[List[str]] = None
    path: Optional[DirectoryPath] = None
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.DataSample

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "owner", "compute_plan_key", "function_key", "dataset_key"]


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
    data_sample_keys: List[str] = []
    opener: _File
    description: _File
    metadata: Dict[str, str]
    creation_date: datetime
    logs_permission: Permission

    type_: ClassVar[str] = schemas.Type.Dataset

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "name", "owner", "permissions", "compute_plan_key", "function_key", "data_sample_key"]


class FunctionInput(_Model):
    identifier: str
    kind: schemas.AssetKind
    optional: bool
    multiple: bool


class FunctionOutput(_Model):
    identifier: str
    kind: schemas.AssetKind
    multiple: bool


class Function(_Model):
    key: str
    name: str
    owner: str
    permissions: Permissions
    metadata: Dict[str, str]
    creation_date: datetime
    inputs: List[FunctionInput]
    outputs: List[FunctionOutput]
    status: FunctionStatus

    description: _File
    archive: _File

    type_: ClassVar[str] = schemas.Type.Function

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "name", "owner", "permissions", "compute_plan_key", "dataset_key", "data_sample_key"]

    @pydantic.field_validator("inputs", mode="before")
    @classmethod
    def dict_input_to_list(cls, v):
        if isinstance(v, dict):
            # Transform the inputs dict to a list
            return [
                FunctionInput(
                    identifier=identifier,
                    kind=function_input["kind"],
                    optional=function_input["optional"],
                    multiple=function_input["multiple"],
                )
                for identifier, function_input in v.items()
            ]
        else:
            return v

    @pydantic.field_validator("outputs", mode="before")
    @classmethod
    def dict_output_to_list(cls, v):
        if isinstance(v, dict):
            # Transform the outputs dict to a list
            return [
                FunctionOutput(
                    identifier=identifier, kind=function_output["kind"], multiple=function_output["multiple"]
                )
                for identifier, function_output in v.items()
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
    address: Optional[InModel] = None
    permissions: Permissions
    owner: str
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Model

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["key", "compute_task_key", "owner", "permissions"]


class InputRef(schemas._PydanticConfig):
    identifier: str
    asset_key: Optional[str] = None
    parent_task_key: Optional[str] = None
    parent_task_output_identifier: Optional[str] = None

    # either (asset_key) or (parent_task_key, parent_task_output_identifier) must be specified
    _check_asset_key_or_parent_ref = pydantic.model_validator(mode="before")(schemas.check_asset_key_or_parent_ref)


class ComputeTaskOutput(schemas._PydanticConfig):
    """Specification of a compute task input"""

    permissions: Permissions
    is_transient: bool = Field(False, alias="transient")
    model_config = ConfigDict(populate_by_name=True)


class Task(_Model):
    key: str
    function: Function
    owner: str
    compute_plan_key: str
    metadata: Dict[str, str]
    status: ComputeTaskStatus
    worker: str
    rank: Optional[int] = None
    tag: str
    creation_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    error_type: Optional[TaskErrorType] = None
    inputs: List[InputRef]
    outputs: Dict[str, ComputeTaskOutput]

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
            "function_key",
        ]


Task.model_rebuild()


class ComputePlan(_Model):
    """ComputePlan"""

    key: str
    tag: str
    name: str
    owner: str
    metadata: Dict[str, str]
    task_count: int = 0
    waiting_builder_slot_count: int = 0
    building_count: int = 0
    waiting_parent_tasks_count: int = 0
    waiting_executor_slot_count: int = 0
    executing_count: int = 0
    canceled_count: int = 0
    failed_count: int = 0
    done_count: int = 0
    failed_task_key: Optional[str] = None
    status: ComputePlanStatus
    creation_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    duration: Optional[int] = None
    creator: Optional[str] = None

    type_: ClassVar[str] = schemas.Type.ComputePlan

    @staticmethod
    def allowed_filters() -> List[str]:
        return [
            "key",
            "name",
            "owner",
            "worker",
            "status",
            "metadata",
            "function_key",
            "dataset_key",
            "data_sample_key",
        ]


class Performances(_Model):
    """Performances of the different compute tasks of a compute plan"""

    compute_plan_key: List[str] = []
    compute_plan_tag: List[str] = []
    compute_plan_status: List[str] = []
    compute_plan_start_date: List[datetime] = []
    compute_plan_end_date: List[datetime] = []
    compute_plan_metadata: List[dict] = []
    worker: List[str] = []
    task_key: List[str] = []
    task_rank: List[int] = []
    round_idx: List[int] = []
    identifier: List[str] = []
    performance: List[float] = []


class Organization(schemas._PydanticConfig):
    """Organization"""

    id: str
    is_current: bool
    creation_date: datetime

    type_: ClassVar[str] = schemas.Type.Organization


class OrganizationInfoConfig(schemas._PydanticConfig, extra="allow"):
    model_config = ConfigDict(protected_namespaces=())
    model_export_enabled: bool


class OrganizationInfo(schemas._PydanticConfig):
    host: AnyUrl
    organization_id: str
    organization_name: str
    config: OrganizationInfoConfig
    channel: str
    version: str
    orchestrator_version: str


class _TaskAsset(schemas._PydanticConfig):
    kind: str
    identifier: str

    @staticmethod
    def allowed_filters() -> List[str]:
        return ["identifier", "kind"]


class InputAsset(_TaskAsset):
    asset: Union[Dataset, DataSample, OutModel]
    type_: ClassVar[str] = schemas.Type.InputAsset


class OutputAsset(_TaskAsset):
    asset: Union[float, OutModel]
    type_: ClassVar[str] = schemas.Type.OutputAsset

    # Deal with remote returning the actual performance object
    @pydantic.field_validator("asset", mode="before")
    @classmethod
    def convert_remote_performance(cls, value, values):
        if values.data.get("kind") == schemas.AssetKind.performance and isinstance(value, dict):
            return value.get("performance_value")

        return value


SCHEMA_TO_MODEL = {
    schemas.Type.Task: Task,
    schemas.Type.Function: Function,
    schemas.Type.ComputePlan: ComputePlan,
    schemas.Type.DataSample: DataSample,
    schemas.Type.Dataset: Dataset,
    schemas.Type.Organization: Organization,
    schemas.Type.Model: OutModel,
    schemas.Type.InputAsset: InputAsset,
    schemas.Type.OutputAsset: OutputAsset,
    schemas.Type.FunctionOutput: FunctionOutput,
    schemas.Type.FunctionInput: FunctionInput,
}
