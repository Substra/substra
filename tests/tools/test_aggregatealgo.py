import json
from os import PathLike
from typing import Any
from typing import List
from typing import TypedDict
from uuid import uuid4

import pytest

from substratools import exceptions
from substratools import function
from substratools import opener
from substratools.task_resources import TaskResources
from substratools.workspace import FunctionWorkspace
from tests.tools import utils
from tests.tools.utils import InputIdentifiers
from tests.tools.utils import OutputIdentifiers


@pytest.fixture(autouse=True)
def setup(valid_opener):
    pass


@function.register
def aggregate(
    inputs: TypedDict(
        "inputs",
        {InputIdentifiers.shared: List[PathLike]},
    ),
    outputs: TypedDict("outputs", {OutputIdentifiers.shared: PathLike}),
    task_properties: TypedDict("task_properties", {InputIdentifiers.rank: int}),
) -> None:
    if inputs:
        models = utils.load_models(paths=inputs.get(InputIdentifiers.shared, []))
    else:
        models = []

    new_model = {"value": 0}
    for m in models:
        new_model["value"] += m["value"]

    utils.save_model(model=new_model, path=outputs.get(OutputIdentifiers.shared))


@function.register
def aggregate_predict(
    inputs: TypedDict(
        "inputs",
        {
            InputIdentifiers.datasamples: Any,
            InputIdentifiers.shared: PathLike,
        },
    ),
    outputs: TypedDict("outputs", {OutputIdentifiers.shared: PathLike}),
    task_properties: TypedDict("task_properties", {InputIdentifiers.rank: int}),
):
    model = utils.load_model(path=inputs.get(OutputIdentifiers.shared))

    # Predict
    X = inputs.get(InputIdentifiers.datasamples)[0]
    pred = X * model["value"]

    # save predictions
    utils.save_predictions(predictions=pred, path=outputs.get(OutputIdentifiers.predictions))


def no_saved_aggregate(inputs, outputs, task_properties):
    if inputs:
        models = utils.load_models(paths=inputs.get(InputIdentifiers.shared, []))
    else:
        models = []

    new_model = {"value": 0}
    for m in models:
        new_model["value"] += m["value"]

    utils.no_save_model(model=new_model, path=outputs.get(OutputIdentifiers.shared))


def wrong_saved_aggregate(inputs, outputs, task_properties):
    if inputs:
        models = utils.load_models(paths=inputs.get(InputIdentifiers.shared, []))
    else:
        models = []

    new_model = {"value": 0}
    for m in models:
        new_model["value"] += m["value"]

    utils.wrong_save_model(model=new_model, path=outputs.get(OutputIdentifiers.shared))


@pytest.fixture
def create_models(workdir):
    model_a = {"value": 1}
    model_b = {"value": 2}

    model_dir = workdir / OutputIdentifiers.shared
    model_dir.mkdir()

    def _create_model(model_data):
        model_name = model_data["value"]
        filename = "{}.json".format(model_name)
        path = model_dir / filename
        path.write_text(json.dumps(model_data))
        return str(path)

    model_datas = [model_a, model_b]
    model_filenames = [_create_model(d) for d in model_datas]

    return model_datas, model_filenames


def test_aggregate_no_model(valid_function_workspace):
    wp = function.FunctionWrapper(workspace=valid_function_workspace, opener_wrapper=None)
    wp.execute(function=aggregate)
    model = utils.load_model(wp._workspace.task_outputs[OutputIdentifiers.shared])
    assert model["value"] == 0


def test_aggregate_multiple_models(create_models, output_model_path):
    _, model_filenames = create_models

    workspace_inputs = TaskResources(
        json.dumps([{"id": InputIdentifiers.shared, "value": f, "multiple": True} for f in model_filenames])
    )
    workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.shared, "value": str(output_model_path), "multiple": False}])
    )

    workspace = FunctionWorkspace(inputs=workspace_inputs, outputs=workspace_outputs)
    wp = function.FunctionWrapper(workspace, opener_wrapper=None)

    wp.execute(function=aggregate)
    model = utils.load_model(wp._workspace.task_outputs[OutputIdentifiers.shared])

    assert model["value"] == 3


@pytest.mark.parametrize(
    "fake_data,expected_pred,n_fake_samples",
    [
        (False, "X", None),
        (True, ["Xfake"], 1),
    ],
)
def test_predict(fake_data, expected_pred, n_fake_samples, create_models):
    _, model_filenames = create_models

    workspace_inputs = TaskResources(
        json.dumps([{"id": InputIdentifiers.shared, "value": model_filenames[0], "multiple": False}])
    )
    workspace_outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.predictions, "value": model_filenames[0], "multiple": False}])
    )

    workspace = FunctionWorkspace(inputs=workspace_inputs, outputs=workspace_outputs)

    wp = function.FunctionWrapper(workspace, opener_wrapper=opener.load_from_module())

    wp.execute(function=aggregate_predict, fake_data=fake_data, n_fake_samples=n_fake_samples)

    pred = utils.load_predictions(wp._workspace.task_outputs[OutputIdentifiers.predictions])
    assert pred == expected_pred


def test_execute_aggregate(output_model_path):
    assert not output_model_path.exists()

    outputs = [{"id": OutputIdentifiers.shared, "value": str(output_model_path), "multiple": False}]

    function.execute(sysargs=["--function-name", "aggregate", "--outputs", json.dumps(outputs)])
    assert output_model_path.exists()
    output_model_path.unlink()
    function.execute(
        sysargs=["--function-name", "aggregate", "--outputs", json.dumps(outputs), "--log-level", "debug"],
    )
    assert output_model_path.exists()


def test_execute_aggregate_multiple_models(workdir, create_models, output_model_path):
    _, model_filenames = create_models

    assert not output_model_path.exists()

    inputs = [
        {"id": InputIdentifiers.shared, "value": str(workdir / model), "multiple": True} for model in model_filenames
    ]
    outputs = [
        {"id": OutputIdentifiers.shared, "value": str(output_model_path), "multiple": False},
    ]
    options = ["--inputs", json.dumps(inputs), "--outputs", json.dumps(outputs)]

    command = ["--function-name", "aggregate"]
    command.extend(options)

    function.execute(sysargs=command)
    assert output_model_path.exists()
    with open(output_model_path, "r") as f:
        model = json.load(f)
    assert model["value"] == 3


def test_execute_predict(workdir, create_models, output_model_path, valid_opener_script):
    _, model_filenames = create_models
    assert not output_model_path.exists()

    inputs = [
        {"id": InputIdentifiers.shared, "value": str(workdir / model_name), "multiple": True}
        for model_name in model_filenames
    ]
    outputs = [{"id": OutputIdentifiers.shared, "value": str(output_model_path), "multiple": False}]
    options = ["--inputs", json.dumps(inputs), "--outputs", json.dumps(outputs)]
    command = ["--function-name", "aggregate"]
    command.extend(options)
    function.execute(sysargs=command)
    assert output_model_path.exists()

    # do predict on output model
    pred_path = workdir / str(uuid4())
    assert not pred_path.exists()

    pred_inputs = [
        {"id": InputIdentifiers.shared, "value": str(output_model_path), "multiple": False},
        {"id": InputIdentifiers.opener, "value": valid_opener_script, "multiple": False},
    ]
    pred_outputs = [{"id": OutputIdentifiers.predictions, "value": str(pred_path), "multiple": False}]
    pred_options = ["--inputs", json.dumps(pred_inputs), "--outputs", json.dumps(pred_outputs)]

    function.execute(sysargs=["--function-name", "predict"] + pred_options)
    assert pred_path.exists()
    with open(pred_path, "r") as f:
        pred = json.load(f)
    assert pred == "XXX"
    pred_path.unlink()


@pytest.mark.parametrize("function_to_run", (no_saved_aggregate, wrong_saved_aggregate))
def test_model_check(function_to_run, valid_function_workspace):
    wp = function.FunctionWrapper(valid_function_workspace, opener_wrapper=None)

    with pytest.raises(exceptions.MissingFileError):
        wp.execute(function=function_to_run)
