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
    Predicttuple = "predicttuple"
    Testtuple = "testtuple"
    Traintuple = "traintuple"
    Aggregatetuple = "aggregatetuple"
    CompositeTraintuple = "composite_traintuple"
    ComputePlan = "compute_plan"
    Organization = "organization"

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
    metric = "ALGO_METRIC"
    predict = "ALGO_PREDICT"


class TaskCategory(str, enum.Enum):
    """Task category"""

    unknown = "TASK_UNKNOWN"
    train = "TASK_TRAIN"
    aggregate = "TASK_AGGREGATE"
    composite = "TASK_COMPOSITE"
    predict = "TASK_PREDICT"
    test = "TASK_TEST"


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
    test_only: bool  # If the data sample is for train or test
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


class _ComputePlanComputeTaskSpec(_Spec):
    """Specification of a compute task inside a compute plan specification"""

    algo_key: str
    tag: Optional[str]
    metadata: Optional[Dict[str, str]]
    inputs: Optional[List[InputRef]]
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]]


class ComputePlanTraintupleSpec(_ComputePlanComputeTaskSpec):
    """Specification of a traintuple inside a compute
    plan specification"""

    data_manager_key: str
    train_data_sample_keys: List[str]
    traintuple_id: str
    in_models_ids: Optional[List[str]]


class ComputePlanAggregatetupleSpec(_ComputePlanComputeTaskSpec):
    """Specification of an aggregate tuple inside a compute
    plan specification"""

    aggregatetuple_id: str
    worker: str
    in_models_ids: Optional[List[str]]


class ComputePlanCompositeTraintupleSpec(_ComputePlanComputeTaskSpec):
    """Specification of a composite traintuple inside a compute
    plan specification"""

    composite_traintuple_id: str
    data_manager_key: str
    train_data_sample_keys: List[str]
    in_head_model_id: Optional[str]
    in_trunk_model_id: Optional[str]


class ComputePlanPredicttupleSpec(_ComputePlanComputeTaskSpec):
    """Specification of a predict tuple inside a compute
    plan specification"""

    predicttuple_id: str
    traintuple_id: str
    data_manager_key: str
    test_data_sample_keys: List[str]


class ComputePlanTesttupleSpec(_ComputePlanComputeTaskSpec):
    """Specification of a testtuple inside a compute
    plan specification"""

    predicttuple_id: str
    data_manager_key: str
    test_data_sample_keys: List[str]


class _BaseComputePlanSpec(_Spec):
    key: str
    traintuples: Optional[List[ComputePlanTraintupleSpec]]
    composite_traintuples: Optional[List[ComputePlanCompositeTraintupleSpec]]
    aggregatetuples: Optional[List[ComputePlanAggregatetupleSpec]]
    predicttuples: Optional[List[ComputePlanPredicttupleSpec]]
    testtuples: Optional[List[ComputePlanTesttupleSpec]]


class ComputePlanSpec(_BaseComputePlanSpec):
    """Specification for creating a compute plan"""

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
    """Specification for creating a dataset"""

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
        if values.get("kind") == AssetKind.data_manager:
            if values.get("multiple"):
                raise ValueError("Data manager input can't be multiple.")
            if values.get("optional"):
                raise ValueError("Data manager input can't be optional.")
            if values.get("identifier") != StaticInputIdentifier.opener:
                raise ValueError(
                    f"Data manager input identifier must be `{StaticInputIdentifier.opener}` "
                    f"but was set to {values['identifier']}"
                )
        elif values.get("kind") == AssetKind.data_sample:
            if values.get("identifier") != StaticInputIdentifier.datasamples:
                raise ValueError(
                    f"Data sample input identifier must be `{StaticInputIdentifier.datasamples}` "
                    f"but was set to {values['identifier']}"
                )

        else:
            if StaticInputIdentifier.has_value(values.get("identifier")):
                raise ValueError(
                    f"Inputs of kind {values.get('kind')} cannot have an identifier among the flowing: "
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
    """Specification for creating an algo"""

    name: str
    description: pathlib.Path
    file: pathlib.Path
    permissions: Permissions
    metadata: Optional[Dict[str, str]]
    category: AlgoCategory
    inputs: Optional[List[AlgoInputSpec]] = None
    outputs: Optional[List[AlgoOutputSpec]] = None

    type_: typing.ClassVar[Type] = Type.Algo

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


class _TupleSpec(_Spec):
    key: str = pydantic.Field(default_factory=lambda: str(uuid.uuid4()))
    tag: Optional[str]
    compute_plan_key: Optional[str]
    metadata: Optional[Dict[str, str]]
    algo_key: str
    inputs: Optional[List[InputRef]]
    outputs: Optional[Dict[str, ComputeTaskOutputSpec]]

    @contextlib.contextmanager
    def build_request_kwargs(self):
        # default values are not dumped when `exclude_unset` flag is enabled,
        # this is why we need to reimplement this custom function.
        data = json.loads(self.json(exclude_unset=True))
        data["key"] = self.key
        data["category"] = self.category
        data["inputs"] = [input.dict() for input in self.inputs] if self.inputs else []
        data["outputs"] = {k: v.dict(by_alias=True) for k, v in self.outputs.items()} if self.outputs else {}
        yield data, None


class TraintupleSpec(_TupleSpec):
    """Specification for creating a traintuple"""

    data_manager_key: str
    train_data_sample_keys: List[str]
    in_models_keys: Optional[List[str]]
    rank: Optional[int]  # Rank of the traintuple in the compute plan
    category: TaskCategory = pydantic.Field(TaskCategory.train, const=True)

    compute_plan_attr_name: typing.ClassVar[str] = "traintuple_keys"
    type_: typing.ClassVar[Type] = Type.Traintuple

    @classmethod
    def from_compute_plan(cls, compute_plan_key: str, rank: int, spec: ComputePlanTraintupleSpec) -> "TraintupleSpec":
        return TraintupleSpec(
            key=spec.traintuple_id,
            algo_key=spec.algo_key,
            data_manager_key=spec.data_manager_key,
            train_data_sample_keys=spec.train_data_sample_keys,
            in_models_keys=spec.in_models_ids or list(),
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata,
        )


class AggregatetupleSpec(_TupleSpec):
    """Specification for creating an aggregate tuple"""

    worker: str
    in_models_keys: List[str]
    rank: Optional[int]
    category: TaskCategory = pydantic.Field(TaskCategory.aggregate, const=True)

    compute_plan_attr_name: typing.ClassVar[str] = "aggregatetuple_keys"
    type_: typing.ClassVar[Type] = Type.Aggregatetuple

    @classmethod
    def from_compute_plan(
        cls, compute_plan_key: str, rank: int, spec: ComputePlanAggregatetupleSpec
    ) -> "AggregatetupleSpec":
        return AggregatetupleSpec(
            key=spec.aggregatetuple_id,
            algo_key=spec.algo_key,
            worker=spec.worker,
            in_models_keys=spec.in_models_ids or list(),
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata,
        )


class CompositeTraintupleSpec(_TupleSpec):
    """Specification for creating a composite traintuple"""

    data_manager_key: str
    train_data_sample_keys: List[str]
    in_head_model_key: Optional[str]
    in_trunk_model_key: Optional[str]
    rank: Optional[int]
    category: TaskCategory = pydantic.Field(TaskCategory.composite, const=True)

    compute_plan_attr_name: typing.ClassVar[str] = "composite_traintuple_keys"
    type_: typing.ClassVar[Type] = Type.CompositeTraintuple

    @classmethod
    def from_compute_plan(
        cls, compute_plan_key: str, rank: int, spec: ComputePlanCompositeTraintupleSpec
    ) -> "CompositeTraintupleSpec":
        return CompositeTraintupleSpec(
            key=spec.composite_traintuple_id,
            algo_key=spec.algo_key,
            data_manager_key=spec.data_manager_key,
            train_data_sample_keys=spec.train_data_sample_keys,
            in_head_model_key=spec.in_head_model_id,
            in_trunk_model_key=spec.in_trunk_model_id,
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            compute_plan_key=compute_plan_key,
            rank=rank,
            metadata=spec.metadata,
        )


class PredicttupleSpec(_TupleSpec):
    """Specification for creating a predict tuple"""

    traintuple_key: str
    data_manager_key: str
    test_data_sample_keys: List[str]
    category: TaskCategory = pydantic.Field(TaskCategory.predict, const=True)

    compute_plan_attr_name: typing.ClassVar[str] = "predicttuple_keys"
    type_: typing.ClassVar[Type] = Type.Predicttuple

    @classmethod
    def from_compute_plan(
        cls, compute_plan_key: str, rank: int, spec: ComputePlanPredicttupleSpec
    ) -> "PredicttupleSpec":
        return PredicttupleSpec(
            key=spec.predicttuple_id,
            algo_key=spec.algo_key,
            traintuple_key=spec.traintuple_id,
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            data_manager_key=spec.data_manager_key,
            test_data_sample_keys=spec.test_data_sample_keys,
            compute_plan_key=compute_plan_key,
            metadata=spec.metadata,
            rank=rank,
        )


class TesttupleSpec(_TupleSpec):
    """Specification for creating a testtuple"""

    predicttuple_key: str
    data_manager_key: str
    test_data_sample_keys: List[str]
    category: TaskCategory = pydantic.Field(TaskCategory.test, const=True)

    type_: typing.ClassVar[Type] = Type.Testtuple

    @classmethod
    def from_compute_plan(cls, compute_plan_key: str, spec: ComputePlanTesttupleSpec) -> "TesttupleSpec":
        return TesttupleSpec(
            algo_key=spec.algo_key,
            predicttuple_key=spec.predicttuple_id,
            inputs=spec.inputs,
            outputs=spec.outputs,
            tag=spec.tag,
            data_manager_key=spec.data_manager_key,
            test_data_sample_keys=spec.test_data_sample_keys,
            compute_plan_key=compute_plan_key,
            metadata=spec.metadata,
        )
