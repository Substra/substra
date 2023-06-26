from enum import Enum

from substra.sdk.schemas import AssetKind
from substra.sdk.schemas import ComputeTaskOutputSpec
from substra.sdk.schemas import FunctionInputSpec
from substra.sdk.schemas import FunctionOutputSpec
from substra.sdk.schemas import InputRef
from substra.sdk.schemas import Permissions

PUBLIC_PERMISSIONS = Permissions(public=True, authorized_ids=[])


class FunctionCategory(str, Enum):
    """Function category"""

    unknown = "FUNCTION_UNKNOWN"
    simple = "FUNCTION_SIMPLE"
    composite = "FUNCTION_COMPOSITE"
    aggregate = "FUNCTION_AGGREGATE"
    metric = "FUNCTION_METRIC"
    predict = "FUNCTION_PREDICT"
    predict_composite = "FUNCTION_PREDICT_COMPOSITE"


class InputIdentifiers(str, Enum):
    local = "local"
    shared = "shared"
    predictions = "predictions"
    performance = "performance"
    opener = "opener"
    datasamples = "datasamples"


class OutputIdentifiers(str, Enum):
    local = "local"
    shared = "shared"
    predictions = "predictions"
    performance = "performance"


class FLFunctionInputs(list, Enum):
    """Substra function inputs by function category based on the InputIdentifiers"""

    FUNCTION_AGGREGATE = [
        FunctionInputSpec(identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=False, multiple=True)
    ]
    FUNCTION_SIMPLE = [
        FunctionInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        FunctionInputSpec(identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=True, multiple=True),
    ]
    FUNCTION_COMPOSITE = [
        FunctionInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        FunctionInputSpec(identifier=InputIdentifiers.local, kind=AssetKind.model.value, optional=True, multiple=False),
        FunctionInputSpec(
            identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=True, multiple=False
        ),
    ]
    FUNCTION_PREDICT = [
        FunctionInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=False, multiple=False
        ),
    ]
    FUNCTION_PREDICT_COMPOSITE = [
        FunctionInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.local, kind=AssetKind.model.value, optional=False, multiple=False
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=False, multiple=False
        ),
    ]
    FUNCTION_METRIC = [
        FunctionInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        FunctionInputSpec(
            identifier=InputIdentifiers.predictions, kind=AssetKind.model.value, optional=False, multiple=False
        ),
    ]


class FLFunctionOutputs(list, Enum):
    """Substra function outputs by function category based on the OutputIdentifiers"""

    FUNCTION_AGGREGATE = [
        FunctionOutputSpec(identifier=OutputIdentifiers.shared, kind=AssetKind.model.value, multiple=False)
    ]
    FUNCTION_SIMPLE = [
        FunctionOutputSpec(identifier=OutputIdentifiers.shared, kind=AssetKind.model.value, multiple=False)
    ]
    FUNCTION_COMPOSITE = [
        FunctionOutputSpec(identifier=OutputIdentifiers.local, kind=AssetKind.model.value, multiple=False),
        FunctionOutputSpec(identifier=OutputIdentifiers.shared, kind=AssetKind.model.value, multiple=False),
    ]
    FUNCTION_PREDICT = [
        FunctionOutputSpec(identifier=OutputIdentifiers.predictions, kind=AssetKind.model.value, multiple=False)
    ]
    FUNCTION_PREDICT_COMPOSITE = [
        FunctionOutputSpec(identifier=OutputIdentifiers.predictions, kind=AssetKind.model.value, multiple=False)
    ]
    FUNCTION_METRIC = [
        FunctionOutputSpec(identifier=OutputIdentifiers.performance, kind=AssetKind.performance.value, multiple=False)
    ]


class FLTaskInputGenerator:
    "Generates task inputs based on Input and OutputIdentifiers"

    @staticmethod
    def opener(opener_key):
        return [InputRef(identifier=InputIdentifiers.opener, asset_key=opener_key)]

    @staticmethod
    def data_samples(data_sample_keys):
        return [
            InputRef(identifier=InputIdentifiers.datasamples, asset_key=data_sample) for data_sample in data_sample_keys
        ]

    @staticmethod
    def task(opener_key, data_sample_keys):
        return FLTaskInputGenerator.opener(opener_key=opener_key) + FLTaskInputGenerator.data_samples(
            data_sample_keys=data_sample_keys
        )

    @staticmethod
    def trains_to_train(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def trains_to_aggregate(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def train_to_predict(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
        ]

    @staticmethod
    def predict_to_test(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.predictions,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.predictions,
            )
        ]

    @staticmethod
    def composite_to_predict(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.local,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.local,
            ),
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            ),
        ]

    @staticmethod
    def composite_to_local(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.local,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.local,
            )
        ]

    @staticmethod
    def composite_to_composite(model1_key, model2_key=None):
        return [
            InputRef(
                identifier=InputIdentifiers.local,
                parent_task_key=model1_key,
                parent_task_output_identifier=OutputIdentifiers.local,
            ),
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model2_key or model1_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            ),
        ]

    @staticmethod
    def aggregate_to_shared(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
        ]

    @staticmethod
    def composites_to_aggregate(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def aggregate_to_predict(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
        ]

    @staticmethod
    def local_to_aggregate(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.local,
            )
        ]

    @staticmethod
    def shared_to_aggregate(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.shared,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
        ]


def _permission_from_ids(authorized_ids):
    if authorized_ids is None:
        return PUBLIC_PERMISSIONS

    return Permissions(public=False, authorized_ids=authorized_ids)


class FLTaskOutputGenerator:
    "Generates task outputs based on Input and OutputIdentifiers"

    @staticmethod
    def traintask(authorized_ids=None):
        return {OutputIdentifiers.shared: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def aggregatetask(authorized_ids=None):
        return {OutputIdentifiers.shared: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def predicttask(authorized_ids=None):
        return {OutputIdentifiers.predictions: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def testtask(authorized_ids=None):
        return {
            OutputIdentifiers.performance: ComputeTaskOutputSpec(
                permissions=Permissions(public=True, authorized_ids=[])
            )
        }

    @staticmethod
    def composite_traintask(shared_authorized_ids=None, local_authorized_ids=None):
        return {
            OutputIdentifiers.shared: ComputeTaskOutputSpec(permissions=_permission_from_ids(shared_authorized_ids)),
            OutputIdentifiers.local: ComputeTaskOutputSpec(permissions=_permission_from_ids(local_authorized_ids)),
        }
