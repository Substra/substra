import contextlib
import enum
import json
import pathlib
import typing
import uuid
from typing import Dict
from typing import List
from typing import Optional

import pydantic
from pydantic import ConfigDict
from pydantic.fields import Field

from substra.sdk import utils

_SERVER_NAMES = {
    "dataset": "data_manager",
    "summary_task": "task",
}


class BackendType(str, enum.Enum):
    REMOTE = "remote"
    LOCAL_DOCKER = "docker"
    LOCAL_SUBPROCESS = "subprocess"


class StaticInputIdentifier(str, enum.Enum):
    chainkeys = "chainkeys"
    datasamples = "datasamples"
    opener = "opener"

    @classmethod
    def values(cls):
        return set(item.value for item in cls)

    @classmethod
    def has_value(cls, value):
        return value in cls.values()


class AssetKind(str, enum.Enum):
    model = "ASSET_MODEL"
    performance = "ASSET_PERFORMANCE"
    data_manager = "ASSET_DATA_MANAGER"
    data_sample = "ASSET_DATA_SAMPLE"


class Type(enum.Enum):
    Function = "function"
    FunctionOutput = "function_output"
    FunctionInput = "function_input"
    DataSample = "data_sample"
    Dataset = "dataset"
    Model = "model"
    ComputePlan = "compute_plan"
    Organization = "organization"
    Task = "task"
    InputAsset = "input_asset"
    OutputAsset = "output_asset"

    def to_server(self):
        """Returns the name used to identify the asset on the backend."""
        name = self.value
        return _SERVER_NAMES.get(name, name)

    def to_asset_kind(self):
        """Returns the name used to identify the asset on the backend."""
        if self.value == self.Dataset.value:
            return AssetKind.data_manager
        else:
            return AssetKind[self.value]

    def __str__(self):
        return self.name


class _PydanticConfig(pydantic.BaseModel):
    """Shared configuration for all schemas here"""

    model_config = ConfigDict(extra="ignore")


class _Spec(_PydanticConfig):
    """Asset creation specification base class."""

    # pretty print
    def __str__(self):
        return self.model_dump_json(indent=4)

    def __repr__(self):
        return self.model_dump_json(indent=4)

    class Meta:
        file_attributes = None

    def is_many(self):
        return False

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # TODO should be located in the backends/remote module
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.model_dump_json(exclude_unset=True))
        if self.Meta.file_attributes:
            with utils.extract_files(data, self.Meta.file_attributes) as (data, files):
                yield (data, files)
        else:
            yield data, None

    @staticmethod
    def compute_key() -> str:
        return str(uuid.uuid4())


class Permissions(_PydanticConfig):
    """Specification for permissions. If public is False,
    give the list of authorized ids.
    """

    public: bool
    authorized_ids: typing.List[str]  # List of authorized organization ids if private


class PrivatePermissions(_PydanticConfig):
    """Specification for private permissions. Only the organizations whose
    ids are in authorized_ids can access the asset.
    """

    authorized_ids: typing.List[str]  # List of authorized organization ids


class DataSampleSpec(_Spec):
    """Specification to create one or many data samples
    To create one data sample, use the 'path' field, otherwise use
    the 'paths' field.
    """

    path: Optional[pathlib.Path] = None  # Path to the data sample if only one
    paths: Optional[List[pathlib.Path]] = None  # Path to the data samples if several
    data_manager_keys: typing.List[str]

    type_: typing.ClassVar[Type] = Type.DataSample

    def is_many(self):
        return self.paths and len(self.paths) > 0

    @pydantic.field_validator("paths")
    @classmethod
    def resolve_paths(cls, v: List[pathlib.Path]) -> List[pathlib.Path]:
        """Resolve given paths."""
        if v is None:
            raise ValueError("'paths' cannot be set to None.")

        return [p.resolve() for p in v]

    @pydantic.field_validator("path")
    @classmethod
    def resolve_path(cls, v: pathlib.Path) -> pathlib.Path:
        """Resolve given path."""
        if v is None:
            raise ValueError("'path' cannot be set to None.")

        return v.resolve()

    @pydantic.model_validator(mode="before")
    @classmethod
    def exclusive_paths(cls, values: typing.Any) -> typing.Any:
        """Check that one and only one path(s) field is defined."""
        if "paths" in values and "path" in values:
            raise ValueError("'path' and 'paths' fields are exclusive.")
        if "paths" not in values and "path" not in values:
            raise ValueError("'path' or 'paths' field must be set.")
        return values

    @contextlib.contextmanager
    def build_request_kwargs(self, local):
        # redefine kwargs builder to handle the local paths
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.model_dump_json(exclude_unset=True))
        if local:
            with utils.extract_data_sample_files(data) as (data, files):
                yield (data, files)
        else:
            yield data, None


def check_asset_key_or_parent_ref(cls, values):
    """Check that either (asset key) or (parent_task_key, parent_task_output_identifier) are set, but not both."""

    has_asset_key = bool(dict(values).get("asset_key"))
    has_parent = bool(dict(values).get("parent_task_key")) and bool(dict(values).get("parent_task_output_identifier"))

    if has_asset_key != has_parent:  # xor
        return values

    raise ValueError("either asset_key or both (parent_task_key, parent_task_output_identifier) must be provided")


class InputRef(_PydanticConfig):
    """Specification of a compute task input"""

    identifier: str
    asset_key: Optional[str] = None
    parent_task_key: Optional[str] = None
    parent_task_output_identifier: Optional[str] = None

    # either (asset_key) or (parent_task_key, parent_task_output_identifier) must be specified
    _check_asset_key_or_parent_ref = pydantic.model_validator(mode="before")(check_asset_key_or_parent_ref)


class ComputeTaskOutputSpec(_PydanticConfig):
    """Specification of a compute task output"""

    permissions: Permissions
    is_transient: Optional[bool] = Field(False, alias="transient")
    model_config = ConfigDict(populate_by_name=True)


class ComputePlanTaskSpec(_Spec):
    """Specification of a compute task inside a compute plan specification

    note : metadata field does not accept strings containing '__' as dict key
    """

    task_id: str
    function_key: str
    worker: str
    tag: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    inputs: Optional[List[InputRef]] = None
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]] = None


class _BaseComputePlanSpec(_Spec):
    key: str
    tasks: Optional[List[ComputePlanTaskSpec]] = None


class ComputePlanSpec(_BaseComputePlanSpec):
    """Specification for creating a compute plan

    note : metadata field does not accept strings containing '__' as dict key
    """

    key: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    tag: Optional[str] = None
    name: str
    metadata: Optional[Dict[str, str]] = None

    type_: typing.ClassVar[Type] = Type.ComputePlan

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # default values are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data = json.loads(self.model_dump_json(exclude_unset=True))
        data["key"] = self.key
        yield data, None


class UpdateComputePlanTasksSpec(_BaseComputePlanSpec):
    """Specification for updating a compute plan's tasks"""

    pass


class UpdateComputePlanSpec(_Spec):
    """Specification for updating a compute plan"""

    name: str

    type_: typing.ClassVar[Type] = Type.ComputePlan


class DatasetSpec(_Spec):
    """Specification for creating a dataset

    note : metadata field does not accept strings containing '__' as dict key
    """

    name: str
    data_opener: pathlib.Path  # Path to the data opener
    type: str
    description: pathlib.Path  # Path to the description file
    permissions: Permissions
    metadata: Optional[Dict[str, str]] = None
    logs_permission: Permissions

    type_: typing.ClassVar[Type] = Type.Dataset

    class Meta:
        file_attributes = (
            "data_opener",
            "description",
        )


class UpdateDatasetSpec(_Spec):
    """Specification for updating a dataset"""

    name: str

    type_: typing.ClassVar[Type] = Type.Dataset


class FunctionInputSpec(_Spec):
    identifier: str
    multiple: bool
    optional: bool
    kind: AssetKind

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_identifiers(cls, values):
        """Checks that the multiplicity and the optionality of a data manager is always set to False"""
        if values["kind"] == AssetKind.data_manager:
            if values["multiple"]:
                raise ValueError("Data manager input can't be multiple.")
            if values["optional"]:
                raise ValueError("Data manager input can't be optional.")
            if values["identifier"] != StaticInputIdentifier.opener:
                raise ValueError(
                    f"Data manager input identifier must be `{StaticInputIdentifier.opener}` "
                    f"but was set to {values['identifier']}"
                )
        elif values["kind"] == AssetKind.data_sample:
            if values["identifier"] != StaticInputIdentifier.datasamples:
                raise ValueError(
                    f"Data sample input identifier must be `{StaticInputIdentifier.datasamples}` "
                    f"but was set to {values['identifier']}"
                )
        else:
            if StaticInputIdentifier.has_value(values["identifier"]):
                raise ValueError(
                    f"Inputs of kind {values['kind']} cannot have an identifier among the flowing: "
                    f"{StaticInputIdentifier.values()}"
                )

        return values


class FunctionOutputSpec(_Spec):
    identifier: str
    kind: AssetKind
    multiple: bool

    @pydantic.model_validator(mode="before")
    @classmethod
    def _check_performance(cls, values):
        """Checks that the performance is always set to False"""
        if values == AssetKind.performance and values["multiple"]:
            raise ValueError("Performance can't be multiple.")

        return values


class FunctionSpec(_Spec):
    """Specification for creating an function

    note : metadata field does not accept strings containing '__' as dict key
    """

    name: str
    description: pathlib.Path
    file: pathlib.Path
    permissions: Permissions
    metadata: Optional[Dict[str, str]] = None
    inputs: Optional[List[FunctionInputSpec]] = None
    outputs: Optional[List[FunctionOutputSpec]] = None

    type_: typing.ClassVar[Type] = Type.Function

    @pydantic.field_validator("inputs")
    @classmethod
    def _check_inputs(cls, v):
        inputs = v or []
        identifiers = {value.identifier for value in inputs}
        if len(identifiers) != len(inputs):
            raise ValueError("Several function inputs cannot have the same identifier.")
        return v

    @pydantic.field_validator("outputs")
    @classmethod
    def _check_outputs(cls, v):
        outputs = v or []
        identifiers = {value.identifier for value in outputs}
        if len(identifiers) != len(outputs):
            raise ValueError("Several function outputs cannot have the same identifier.")
        return v

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # TODO should be located in the backends/remote module
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.model_dump_json(exclude_unset=True))

        # Computed fields using `@property` are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data["inputs"] = (
            {input.identifier: input.model_dump(exclude={"identifier"}) for input in self.inputs}
            if self.inputs
            else dict()
        )
        data["outputs"] = (
            {output.identifier: output.model_dump(exclude={"identifier"}) for output in self.outputs}
            if self.outputs
            else dict()
        )

        if self.Meta.file_attributes:
            with utils.extract_files(data, self.Meta.file_attributes) as (data, files):
                yield (data, files)
        else:
            yield data, None

    class Meta:
        file_attributes = (
            "file",
            "description",
        )


class UpdateFunctionSpec(_Spec):
    """Specification for updating an function"""

    name: str

    type_: typing.ClassVar[Type] = Type.Function


class TaskSpec(_Spec):
    key: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    tag: Optional[str] = None
    compute_plan_key: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None
    function_key: str
    worker: str
    rank: Optional[int] = None
    inputs: Optional[List[InputRef]] = None
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]] = None

    type_: typing.ClassVar[Type] = Type.Task

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # default values are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data = json.loads(self.model_dump_json(exclude_unset=True))
        data["key"] = self.key
        data["inputs"] = [input.model_dump() for input in self.inputs] if self.inputs else []
        data["outputs"] = {k: v.model_dump(by_alias=True) for k, v in self.outputs.items()} if self.outputs else {}
        yield data, None

    @classmethod
    def from_compute_plan(cls, compute_plan_key: str, rank: int, spec: ComputePlanTaskSpec) -> "TaskSpec":
        return TaskSpec(
            key=spec.task_id,
            function_key=spec.function_key,
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata,
            worker=spec.worker,
        )
