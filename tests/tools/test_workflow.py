import json
import os

import pytest

from substratools import load_performance
from substratools import opener
from substratools import save_performance
from substratools.function import FunctionWrapper
from substratools.task_resources import TaskResources
from substratools.utils import import_module
from substratools.workspace import FunctionWorkspace
from tests.tools import utils
from tests.tools.utils import InputIdentifiers
from tests.tools.utils import OutputIdentifiers


@pytest.fixture
def dummy_opener():
    script = """
import json
from substratools import Opener

class DummyOpener(Opener):
    def get_data(self, folder):
        return None

    def fake_data(self, n_samples):
        raise NotImplementedError
"""
    import_module("opener", script)


def train(inputs, outputs, task_properties):
    models = utils.load_models(inputs.get(InputIdentifiers.shared, []))
    total = sum([m["i"] for m in models])
    new_model = {"i": len(models) + 1, "total": total}

    utils.save_model(new_model, outputs.get(OutputIdentifiers.shared))


def predict(inputs, outputs, task_properties):
    model = utils.load_model(inputs.get(InputIdentifiers.shared))
    pred = {"sum": model["i"]}
    utils.save_predictions(pred, outputs.get(OutputIdentifiers.predictions))


def score(inputs, outputs, task_properties):
    y_pred_path = inputs.get(InputIdentifiers.predictions)
    y_pred = utils.load_predictions(y_pred_path)

    score = y_pred["sum"]

    save_performance(performance=score, path=outputs.get(OutputIdentifiers.performance))


def test_workflow(workdir, dummy_opener):
    loop1_model_path = workdir / "loop1model"
    loop1_workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.shared, "value": str(loop1_model_path), "multiple": False}])
    )
    loop1_workspace = FunctionWorkspace(outputs=loop1_workspace_outputs)
    loop1_wp = FunctionWrapper(workspace=loop1_workspace, opener_wrapper=None)

    # loop 1 (no input)
    loop1_wp.execute(function=train)
    model = utils.load_model(path=loop1_wp._workspace.task_outputs[OutputIdentifiers.shared])

    assert model == {"i": 1, "total": 0}
    assert os.path.exists(loop1_model_path)

    loop2_model_path = workdir / "loop2model"

    loop2_workspace_inputs = TaskResources(
        json.dumps([{"id": InputIdentifiers.shared, "value": str(loop1_model_path), "multiple": True}])
    )
    loop2_workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.shared, "value": str(loop2_model_path), "multiple": False}])
    )
    loop2_workspace = FunctionWorkspace(inputs=loop2_workspace_inputs, outputs=loop2_workspace_outputs)
    loop2_wp = FunctionWrapper(workspace=loop2_workspace, opener_wrapper=None)

    # loop 2 (one model as input)
    loop2_wp.execute(function=train)
    model = utils.load_model(path=loop2_wp._workspace.task_outputs[OutputIdentifiers.shared])
    assert model == {"i": 2, "total": 1}
    assert os.path.exists(loop2_model_path)

    loop3_model_path = workdir / "loop2model"
    loop3_workspace_inputs = TaskResources(
        json.dumps(
            [
                {"id": InputIdentifiers.shared, "value": str(loop1_model_path), "multiple": True},
                {"id": InputIdentifiers.shared, "value": str(loop2_model_path), "multiple": True},
            ]
        )
    )
    loop3_workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.shared, "value": str(loop3_model_path), "multiple": False}])
    )
    loop3_workspace = FunctionWorkspace(inputs=loop3_workspace_inputs, outputs=loop3_workspace_outputs)
    loop3_wp = FunctionWrapper(workspace=loop3_workspace, opener_wrapper=None)

    # loop 3 (two models as input)
    loop3_wp.execute(function=train)
    model = utils.load_model(path=loop3_wp._workspace.task_outputs[OutputIdentifiers.shared])
    assert model == {"i": 3, "total": 3}
    assert os.path.exists(loop3_model_path)

    predictions_path = workdir / "predictions"
    predict_workspace_inputs = TaskResources(
        json.dumps([{"id": InputIdentifiers.shared, "value": str(loop3_model_path), "multiple": False}])
    )
    predict_workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.predictions, "value": str(predictions_path), "multiple": False}])
    )
    predict_workspace = FunctionWorkspace(inputs=predict_workspace_inputs, outputs=predict_workspace_outputs)
    predict_wp = FunctionWrapper(workspace=predict_workspace, opener_wrapper=None)

    # predict
    predict_wp.execute(function=predict)
    pred = utils.load_predictions(path=predict_wp._workspace.task_outputs[OutputIdentifiers.predictions])
    assert pred == {"sum": 3}

    # metrics
    performance_path = workdir / "performance"
    metric_workspace_inputs = TaskResources(
        json.dumps([{"id": InputIdentifiers.predictions, "value": str(predictions_path), "multiple": False}])
    )
    metric_workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.performance, "value": str(performance_path), "multiple": False}])
    )
    metric_workspace = FunctionWorkspace(
        inputs=metric_workspace_inputs,
        outputs=metric_workspace_outputs,
    )
    metrics_wp = FunctionWrapper(workspace=metric_workspace, opener_wrapper=opener.load_from_module())
    metrics_wp.execute(function=score)
    res = load_performance(path=metrics_wp._workspace.task_outputs[OutputIdentifiers.performance])
    assert res == 3.0
