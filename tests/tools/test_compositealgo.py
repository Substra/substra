import json
import os
from typing import Any
from typing import Optional
from typing import TypedDict

import pytest

from substratools import exceptions
from substratools import function
from substratools import opener
from substratools.task_resources import TaskResources
from substratools.workspace import FunctionWorkspace
from tests.tools import utils
from tests.utils import InputIdentifiers
from tests.utils import OutputIdentifiers


@pytest.fixture(autouse=True)
def setup(valid_opener):
    pass


def fake_data_train(inputs: dict, outputs: dict, task_properties: dict):
    utils.save_model(model=inputs[InputIdentifiers.datasamples][0], path=outputs["local"])
    utils.save_model(model=inputs[InputIdentifiers.datasamples][1], path=outputs["shared"])


def fake_data_predict(inputs: dict, outputs: dict, task_properties: dict) -> None:
    utils.save_model(model=inputs[InputIdentifiers.datasamples][0], path=outputs["predictions"])


def train(
    inputs: TypedDict(
        "inputs",
        {
            InputIdentifiers.datasamples: Any,
            InputIdentifiers.local: Optional[os.PathLike],
            InputIdentifiers.shared: Optional[os.PathLike],
        },
    ),
    outputs: TypedDict(
        "outputs",
        {
            OutputIdentifiers.local: os.PathLike,
            OutputIdentifiers.shared: os.PathLike,
        },
    ),
    task_properties: TypedDict("task_properties", {InputIdentifiers.rank: int}),
):
    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    if head_model and trunk_model:
        new_head_model = dict(head_model)
        new_trunk_model = dict(trunk_model)
    else:
        new_head_model = {"value": 0}
        new_trunk_model = {"value": 0}

    # train models
    new_head_model["value"] += 1
    new_trunk_model["value"] -= 1

    # save model
    utils.save_model(model=new_head_model, path=outputs.get(OutputIdentifiers.local))
    utils.save_model(model=new_trunk_model, path=outputs.get(OutputIdentifiers.shared))


def predict(
    inputs: TypedDict(
        "inputs",
        {
            InputIdentifiers.datasamples: Any,
            InputIdentifiers.local: os.PathLike,
            InputIdentifiers.shared: os.PathLike,
        },
    ),
    outputs: TypedDict(
        "outputs",
        {
            OutputIdentifiers.predictions: os.PathLike,
        },
    ),
    task_properties: TypedDict("task_properties", {InputIdentifiers.rank: int}),
):

    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    pred = list(range(head_model["value"], trunk_model["value"]))

    # save predictions
    utils.save_predictions(predictions=pred, path=outputs.get(OutputIdentifiers.predictions))


def no_saved_trunk_train(inputs, outputs, task_properties):
    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    if head_model and trunk_model:
        new_head_model = dict(head_model)
        new_trunk_model = dict(trunk_model)
    else:
        new_head_model = {"value": 0}
        new_trunk_model = {"value": 0}

    # train models
    new_head_model["value"] += 1
    new_trunk_model["value"] -= 1

    # save model
    utils.save_model(model=new_head_model, path=outputs.get(OutputIdentifiers.local))
    utils.no_save_model(model=new_trunk_model, path=outputs.get(OutputIdentifiers.shared))


def no_saved_head_train(inputs, outputs, task_properties):
    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    if head_model and trunk_model:
        new_head_model = dict(head_model)
        new_trunk_model = dict(trunk_model)
    else:
        new_head_model = {"value": 0}
        new_trunk_model = {"value": 0}

    # train models
    new_head_model["value"] += 1
    new_trunk_model["value"] -= 1

    # save model
    utils.no_save_model(model=new_head_model, path=outputs.get(OutputIdentifiers.local))
    utils.save_model(model=new_trunk_model, path=outputs.get(OutputIdentifiers.shared))


def wrong_saved_trunk_train(inputs, outputs, task_properties):
    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    if head_model and trunk_model:
        new_head_model = dict(head_model)
        new_trunk_model = dict(trunk_model)
    else:
        new_head_model = {"value": 0}
        new_trunk_model = {"value": 0}

    # train models
    new_head_model["value"] += 1
    new_trunk_model["value"] -= 1

    # save model
    utils.save_model(model=new_head_model, path=outputs.get(OutputIdentifiers.local))
    utils.wrong_save_model(model=new_trunk_model, path=outputs.get(OutputIdentifiers.shared))


def wrong_saved_head_train(inputs, outputs, task_properties):
    # init phase
    # load models
    head_model = utils.load_model(path=inputs.get(InputIdentifiers.local))
    trunk_model = utils.load_model(path=inputs.get(InputIdentifiers.shared))

    if head_model and trunk_model:
        new_head_model = dict(head_model)
        new_trunk_model = dict(trunk_model)
    else:
        new_head_model = {"value": 0}
        new_trunk_model = {"value": 0}

    # train models
    new_head_model["value"] += 1
    new_trunk_model["value"] -= 1

    # save model
    utils.wrong_save_model(model=new_head_model, path=outputs.get(OutputIdentifiers.local))
    utils.save_model(model=new_trunk_model, path=outputs.get(OutputIdentifiers.shared))


@pytest.fixture
def train_outputs(output_model_path, output_model_path_2):
    outputs = TaskResources(
        json.dumps(
            [
                {"id": "local", "value": str(output_model_path), "multiple": False},
                {"id": "shared", "value": str(output_model_path_2), "multiple": False},
            ]
        )
    )
    return outputs


@pytest.fixture
def composite_inputs(create_models):
    _, local_path, shared_path = create_models
    inputs = TaskResources(
        json.dumps(
            [
                {"id": InputIdentifiers.local, "value": str(local_path), "multiple": False},
                {"id": InputIdentifiers.shared, "value": str(shared_path), "multiple": False},
            ]
        )
    )

    return inputs


@pytest.fixture
def predict_outputs(output_model_path):
    outputs = TaskResources(
        json.dumps([{"id": OutputIdentifiers.predictions, "value": str(output_model_path), "multiple": False}])
    )
    return outputs


@pytest.fixture
def create_models(workdir):
    head_model = {"value": 1}
    trunk_model = {"value": -1}

    def _create_model(model_data, name):
        filename = "{}.json".format(name)
        path = workdir / filename
        path.write_text(json.dumps(model_data))
        return path

    head_path = _create_model(head_model, "head")
    trunk_path = _create_model(trunk_model, "trunk")

    return (
        [head_model, trunk_model],
        head_path,
        trunk_path,
    )


def test_train_no_model(train_outputs):

    dummy_train_workspace = FunctionWorkspace(outputs=train_outputs)
    dummy_train_wrapper = function.FunctionWrapper(dummy_train_workspace, None)
    dummy_train_wrapper.execute(function=train)
    local_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs["local"])
    shared_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs["shared"])

    assert local_model["value"] == 1
    assert shared_model["value"] == -1


def test_train_input_head_trunk_models(composite_inputs, train_outputs):

    dummy_train_workspace = FunctionWorkspace(inputs=composite_inputs, outputs=train_outputs)
    dummy_train_wrapper = function.FunctionWrapper(dummy_train_workspace, None)
    dummy_train_wrapper.execute(function=train)
    local_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs["local"])
    shared_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs["shared"])

    assert local_model["value"] == 2
    assert shared_model["value"] == -2


@pytest.mark.parametrize("n_fake_samples", (0, 1, 2))
def test_train_fake_data(train_outputs, n_fake_samples):
    _opener = opener.load_from_module()
    dummy_train_workspace = FunctionWorkspace(outputs=train_outputs)
    dummy_train_wrapper = function.FunctionWrapper(dummy_train_workspace, _opener)
    dummy_train_wrapper.execute(function=fake_data_train, fake_data=bool(n_fake_samples), n_fake_samples=n_fake_samples)

    local_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs[OutputIdentifiers.local])
    shared_model = utils.load_model(dummy_train_wrapper._workspace.task_outputs[OutputIdentifiers.shared])

    assert local_model == _opener.get_data(fake_data=bool(n_fake_samples), n_fake_samples=n_fake_samples)[0]
    assert shared_model == _opener.get_data(fake_data=bool(n_fake_samples), n_fake_samples=n_fake_samples)[1]


@pytest.mark.parametrize("n_fake_samples", (0, 1, 2))
def test_predict_fake_data(composite_inputs, predict_outputs, n_fake_samples):
    _opener = opener.load_from_module()
    dummy_train_workspace = FunctionWorkspace(inputs=composite_inputs, outputs=predict_outputs)
    dummy_train_wrapper = function.FunctionWrapper(dummy_train_workspace, _opener)
    dummy_train_wrapper.execute(
        function=fake_data_predict, fake_data=bool(n_fake_samples), n_fake_samples=n_fake_samples
    )

    predictions = utils.load_model(dummy_train_wrapper._workspace.task_outputs[OutputIdentifiers.predictions])

    assert predictions == _opener.get_data(fake_data=bool(n_fake_samples), n_fake_samples=n_fake_samples)[0]


@pytest.mark.parametrize(
    "function_to_run",
    (
        no_saved_head_train,
        no_saved_trunk_train,
        wrong_saved_head_train,
        wrong_saved_trunk_train,
    ),
)
def test_model_check(function_to_run, train_outputs):
    dummy_train_workspace = FunctionWorkspace(outputs=train_outputs)
    wp = function.FunctionWrapper(workspace=dummy_train_workspace, opener_wrapper=None)

    with pytest.raises(exceptions.MissingFileError):
        wp.execute(function_to_run)
