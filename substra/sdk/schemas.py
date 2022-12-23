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
from pydantic.fields import Field

from substra.sdk import utils

_SERVER_NAMES = {
    "dataset": "data_manager",
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
    Algo = "algo"
    DataSample = "data_sample"
    Dataset = "dataset"
    Model = "model"
    ComputePlan = "compute_plan"
    Organization = "organization"
    Task = "task"

    def to_server(self):
        """Returns the name used to identify the asset on the backend."""
        name = self.value
        return _SERVER_NAMES.get(name, name)

    def __str__(self):
        return self.name


class _PydanticConfig(pydantic.BaseModel):
    """Shared configuration for all schemas here"""

    class Config:
        # Ignore extra fields, leave them unexposed
        extra = "ignore"


class _Spec(_PydanticConfig):
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

    path: Optional[pathlib.Path]  # Path to the data sample if only one
    paths: Optional[List[pathlib.Path]]  # Path to the data samples if several
    data_manager_keys: typing.List[str]

    type_: typing.ClassVar[Type] = Type.DataSample

    def is_many(self):
        return self.paths and len(self.paths) > 0

    @pydantic.root_validator(pre=True)
    def exclusive_paths(cls, values):  # noqa: N805
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
        data = json.loads(self.json(exclude_unset=True))
        if local:
            with utils.extract_data_sample_files(data) as (data, files):
                yield (data, files)
        else:
            yield data, None


def check_asset_key_or_parent_ref(cls, values):
    """Check that either (asset key) or (parent_task_key, parent_task_output_identifier) are set, but not both."""

    has_asset_key = bool(values.get("asset_key"))
    has_parent = bool(values.get("parent_task_key")) and bool(values.get("parent_task_output_identifier"))

    if has_asset_key != has_parent:  # xor
        return values

    raise ValueError("either asset_key or both (parent_task_key, parent_task_output_identifier) must be provided")


class InputRef(_PydanticConfig):
    """Specification of a compute task input"""

    identifier: str
    asset_key: Optional[str]
    parent_task_key: Optional[str]
    parent_task_output_identifier: Optional[str]

    # either (asset_key) or (parent_task_key, parent_task_output_identifier) must be specified
    _check_asset_key_or_parent_ref = pydantic.root_validator(allow_reuse=True)(check_asset_key_or_parent_ref)


class ComputeTaskOutputSpec(_PydanticConfig):
    """Specification of a compute task output"""

    permissions: Permissions
    is_transient: Optional[bool] = Field(False, alias="transient")

    class Config:
        allow_population_by_field_name = True


class ComputePlanTaskSpec(_Spec):
    """Specification of a compute task inside a compute plan specification

    note : metadata field does not accept strings containing '__' as dict key
    """

    task_id: str
    algo_key: str
    worker: str
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]
    inputs: Optional[List[InputRef]]
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]]


class _BaseComputePlanSpec(_Spec):
    key: str
    tasks: Optional[List[ComputePlanTaskSpec]]


class ComputePlanSpec(_BaseComputePlanSpec):
    """Specification for creating a compute plan

    note : metadata field does not accept strings containing '__' as dict key
    """

    key: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    tag: Optional[str]
    name: str
    metadata: Optional[Dict[str, str]]

    type_: typing.ClassVar[Type] = Type.ComputePlan

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # default values are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data = json.loads(self.json(exclude_unset=True))
        data["key"] = self.key
        yield data, None


class UpdateComputePlanTuplesSpec(_BaseComputePlanSpec):
    """Specification for updating a compute plan's tuples"""

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
    metadata: Optional[Dict[str, str]]
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


class AlgoInputSpec(_Spec):
    identifier: str
    multiple: bool
    optional: bool
    kind: AssetKind

    @pydantic.root_validator
    def _check_identifiers(cls, values):  # noqa: N805
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


class AlgoOutputSpec(_Spec):
    identifier: str
    kind: AssetKind
    multiple: bool

    @pydantic.root_validator
    def _check_performance(cls, values):  # noqa: N805
        """Checks that the performance is always set to False"""
        if values.get("kind") == AssetKind.performance and values.get("multiple"):
            raise ValueError("Performance can't be multiple.")

        return values


class AlgoSpec(_Spec):
    """Specification for creating an algo

    note : metadata field does not accept strings containing '__' as dict key
    """

    name: str
    description: pathlib.Path
    file: pathlib.Path
    permissions: Permissions
    metadata: Optional[Dict[str, str]]
    inputs: Optional[List[AlgoInputSpec]] = None
    outputs: Optional[List[AlgoOutputSpec]] = None

    type_: typing.ClassVar[Type] = Type.Algo

    @pydantic.validator("inputs")
    def _check_inputs(cls, v):  # noqa: N805
        inputs = v or list()
        identifiers = {value.identifier for value in inputs}
        if len(identifiers) != len(inputs):
            raise ValueError("Several algo inputs cannot have the same identifier.")
        return v

    @pydantic.validator("outputs")
    def _check_outputs(cls, v):  # noqa: N805
        outputs = v or list()
        identifiers = {value.identifier for value in outputs}
        if len(identifiers) != len(outputs):
            raise ValueError("Several algo outputs cannot have the same identifier.")
        return v

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # TODO should be located in the backends/remote module
        # Serialize and deserialize to prevent errors eg with pathlib.Path
        data = json.loads(self.json(exclude_unset=True))

        # Computed fields using `@property` are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data["inputs"] = (
            {input.identifier: input.dict(exclude={"identifier"}) for input in self.inputs} if self.inputs else {}
        )
        data["outputs"] = (
            {output.identifier: output.dict(exclude={"identifier"}) for output in self.outputs} if self.outputs else {}
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


class UpdateAlgoSpec(_Spec):
    """Specification for updating an algo"""

    name: str

    type_: typing.ClassVar[Type] = Type.Algo


class TaskSpec(_Spec):
    key: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    tag: Optional[str]
    compute_plan_key: Optional[str]
    metadata: Optional[Dict[str, str]]
    algo_key: str
    worker: str
    rank: Optional[int] = None
    inputs: Optional[List[InputRef]]
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]]

    type_: typing.ClassVar[Type] = Type.Task

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # default values are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data = json.loads(self.json(exclude_unset=True))
        data["key"] = self.key
        data["inputs"] = [input.dict() for input in self.inputs] if self.inputs else []
        data["outputs"] = {k: v.dict(by_alias=True) for k, v in self.outputs.items()} if self.outputs else {}
        yield data, None

    @classmethod
    def from_compute_plan(cls, compute_plan_key: str, rank: int, spec: ComputePlanTaskSpec) -> "TaskSpec":
        return TaskSpec(
            key=spec.task_id,
            algo_key=spec.algo_key,
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata,
            worker=spec.worker,
        )
