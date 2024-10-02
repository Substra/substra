import json

import pytest

from substratools.exceptions import InvalidCLIError
from substratools.exceptions import InvalidInputOutputsError
from substratools.task_resources import StaticInputIdentifiers
from substratools.task_resources import TaskResources

_VALID_RESOURCES = [
    {"id": "foo", "value": "bar", "multiple": True},
    {"id": "foo", "value": "babar", "multiple": True},
    {"id": "fofo", "value": "bar", "multiple": False},
]
_VALID_VALUES = {"foo": {"value": ["bar", "babar"], "multiple": True}, "fofo": {"value": ["bar"], "multiple": False}}


@pytest.mark.parametrize(
    "invalid_arg",
    (
        {"foo": "barr"},
        "foo and bar",
        ["foo", "barr"],
        [{"foo": "bar"}],
        [{"foo": "bar"}, {"id": "foo", "value": "bar", "multiple": True}],
        # [{_RESOURCE_ID: "foo", _RESOURCE_VALUE: "some path", _RESOURCE_MULTIPLE: "str"}],
    ),
)
def test_task_resources_invalid_argsrt(invalid_arg):
    with pytest.raises(InvalidCLIError):
        TaskResources(json.dumps(invalid_arg))


@pytest.mark.parametrize(
    "valid_arg,expected",
    [
        ([], {}),
        ([{"id": "foo", "value": "bar", "multiple": True}], {"foo": {"value": ["bar"], "multiple": True}}),
        (
            [{"id": "foo", "value": "bar", "multiple": True}, {"id": "foo", "value": "babar", "multiple": True}],
            {"foo": {"value": ["bar", "babar"], "multiple": True}},
        ),
        (_VALID_RESOURCES, _VALID_VALUES),
    ],
)
def test_task_resources_values(valid_arg, expected):
    TaskResources(json.dumps(valid_arg))._values == expected


@pytest.mark.parametrize(
    "static_resource_id",
    (
        StaticInputIdentifiers.chainkeys.value,
        StaticInputIdentifiers.datasamples.value,
        StaticInputIdentifiers.opener.value,
    ),
)
def test_task_static_resources(static_resource_id):
    "checks that static keys opener, datasamples and chainkeys are excluded"

    TaskResources(
        json.dumps(_VALID_RESOURCES + [{"id": static_resource_id, "value": "foo", "multiple": False}])
    )._values == _VALID_VALUES


@pytest.mark.parametrize("key", tuple(_VALID_VALUES.keys()))
def test_get_value(key):
    "get_value method returns a list of path of multiple resource and a path for non multiple ones"
    expected = _VALID_VALUES[key]["value"]

    if _VALID_VALUES[key]["multiple"]:
        expected = expected[0]


def test_multiple_resource_error():
    "non multiple resource can't have multiple values"

    with pytest.raises(InvalidInputOutputsError):
        TaskResources(
            json.dumps(
                [
                    {"id": "foo", "value": "bar", "multiple": False},
                    {"id": "foo", "value": "babar", "multiple": False},
                ]
            )
        )
