from enum import Enum

from substra.sdk.schemas import AlgoInputSpec
from substra.sdk.schemas import AlgoOutputSpec
from substra.sdk.schemas import AssetKind
from substra.sdk.schemas import ComputeTaskOutputSpec
from substra.sdk.schemas import InputRef
from substra.sdk.schemas import Permissions

PUBLIC_PERMISSIONS = Permissions(public=True, authorized_ids=[])


class AlgoCategory(str, Enum):
    """Algo category"""

    unknown = "ALGO_UNKNOWN"
    simple = "ALGO_SIMPLE"
    composite = "ALGO_COMPOSITE"
    aggregate = "ALGO_AGGREGATE"
    metric = "ALGO_METRIC"
    predict = "ALGO_PREDICT"
    predict_composite = "ALGO_PREDICT_COMPOSITE"


class InputIdentifiers(str, Enum):
    local = "local"
    shared = "shared"
    model = "model"
    models = "models"
    predictions = "predictions"
    performance = "performance"
    opener = "opener"
    datasamples = "datasamples"


class OutputIdentifiers(str, Enum):
    local = "local"
    shared = "shared"
    model = "model"
    predictions = "predictions"
    performance = "performance"


class FLAlgoInputs(list, Enum):
    """Substra algo inputs by algo category based on the InputIdentifiers"""

    ALGO_AGGREGATE = [
        AlgoInputSpec(identifier=InputIdentifiers.models, kind=AssetKind.model.value, optional=False, multiple=True)
    ]
    ALGO_SIMPLE = [
        AlgoInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        AlgoInputSpec(identifier=InputIdentifiers.models, kind=AssetKind.model.value, optional=True, multiple=True),
    ]
    ALGO_COMPOSITE = [
        AlgoInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        AlgoInputSpec(identifier=InputIdentifiers.local, kind=AssetKind.model.value, optional=True, multiple=False),
        AlgoInputSpec(identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=True, multiple=False),
    ]
    ALGO_PREDICT = [
        AlgoInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        AlgoInputSpec(identifier=InputIdentifiers.model, kind=AssetKind.model.value, optional=False, multiple=False),
    ]
    ALGO_PREDICT_COMPOSITE = [
        AlgoInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        AlgoInputSpec(identifier=InputIdentifiers.local, kind=AssetKind.model.value, optional=False, multiple=False),
        AlgoInputSpec(identifier=InputIdentifiers.shared, kind=AssetKind.model.value, optional=False, multiple=False),
    ]
    ALGO_METRIC = [
        AlgoInputSpec(
            identifier=InputIdentifiers.datasamples,
            kind=AssetKind.data_sample.value,
            optional=False,
            multiple=True,
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.opener, kind=AssetKind.data_manager.value, optional=False, multiple=False
        ),
        AlgoInputSpec(
            identifier=InputIdentifiers.predictions, kind=AssetKind.model.value, optional=False, multiple=False
        ),
    ]


class FLAlgoOutputs(list, Enum):
    """Substra algo outputs by algo category based on the OutputIdentifiers"""

    ALGO_AGGREGATE = [AlgoOutputSpec(identifier=OutputIdentifiers.model, kind=AssetKind.model.value, multiple=False)]
    ALGO_SIMPLE = [AlgoOutputSpec(identifier=OutputIdentifiers.model, kind=AssetKind.model.value, multiple=False)]
    ALGO_COMPOSITE = [
        AlgoOutputSpec(identifier=OutputIdentifiers.local, kind=AssetKind.model.value, multiple=False),
        AlgoOutputSpec(identifier=OutputIdentifiers.shared, kind=AssetKind.model.value, multiple=False),
    ]
    ALGO_PREDICT = [
        AlgoOutputSpec(identifier=OutputIdentifiers.predictions, kind=AssetKind.model.value, multiple=False)
    ]
    ALGO_PREDICT_COMPOSITE = [
        AlgoOutputSpec(identifier=OutputIdentifiers.predictions, kind=AssetKind.model.value, multiple=False)
    ]
    ALGO_METRIC = [
        AlgoOutputSpec(identifier=OutputIdentifiers.performance, kind=AssetKind.performance.value, multiple=False)
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
    def tuple(opener_key, data_sample_keys):
        return FLTaskInputGenerator.opener(opener_key=opener_key) + FLTaskInputGenerator.data_samples(
            data_sample_keys=data_sample_keys
        )

    @staticmethod
    def trains_to_train(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.model,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def trains_to_aggregate(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.model,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def train_to_predict(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.model,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.model,
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
                parent_task_output_identifier=OutputIdentifiers.model,
            )
        ]

    @staticmethod
    def composites_to_aggregate(model_keys):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.shared,
            )
            for model_key in model_keys
        ]

    @staticmethod
    def aggregate_to_predict(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.model,
            )
        ]

    @staticmethod
    def local_to_aggregate(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
                parent_task_key=model_key,
                parent_task_output_identifier=OutputIdentifiers.local,
            )
        ]

    @staticmethod
    def shared_to_aggregate(model_key):
        return [
            InputRef(
                identifier=InputIdentifiers.models,
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
    def traintuple(authorized_ids=None):
        return {OutputIdentifiers.model: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def aggregatetuple(authorized_ids=None):
        return {OutputIdentifiers.model: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def predicttuple(authorized_ids=None):
        return {OutputIdentifiers.predictions: ComputeTaskOutputSpec(permissions=_permission_from_ids(authorized_ids))}

    @staticmethod
    def testtuple(authorized_ids=None):
        return {
            OutputIdentifiers.performance: ComputeTaskOutputSpec(
                permissions=Permissions(public=True, authorized_ids=[])
            )
        }

    @staticmethod
    def composite_traintuple(shared_authorized_ids=None, local_authorized_ids=None):
        return {
            OutputIdentifiers.shared: ComputeTaskOutputSpec(permissions=_permission_from_ids(shared_authorized_ids)),
            OutputIdentifiers.local: ComputeTaskOutputSpec(permissions=_permission_from_ids(local_authorized_ids)),
        }
