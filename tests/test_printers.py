import pytest

from substra.cli import printers


@pytest.mark.parametrize(
    "obj,path,res",
    [
        ({}, "a", None),
        ({}, "a.b", None),
        ({"a": None}, "a.b", None),
        ({"a": "a"}, "a", "a"),
        ({"a": {"b": "b"}}, "a.b", "b"),
    ],
)
def test_find_dict_composite_key_value(obj, path, res):
    assert printers.find_dict_composite_key_value(obj, path) == res


def test_find_dict_composite_key_value_fails():
    with pytest.raises(AttributeError):
        printers.find_dict_composite_key_value({"a": "b"}, "a.b")
