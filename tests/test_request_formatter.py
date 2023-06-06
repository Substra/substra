import pytest

from substra.sdk.backends.remote import request_formatter


@pytest.mark.parametrize(
    "raw,formatted",
    [
        ({"foo": ["bar", "baz"]}, {"foo": "bar,baz"}),
        ({"foo": ["bar", "baz"], "bar": ["qux"]}, {"foo": "bar,baz", "bar": "qux"}),
        ({"foo": ["b ar ", " baz"]}, {"foo": "bar,baz"}),
        (
            {},
            {},
        ),
        ({"name": "bar,baz"}, {"match": "bar,baz"}),
        (
            {"metadata": [{"key": "epochs", "type": "is", "value": "10"}]},
            {"metadata": '[{"key":"epochs","type":"is","value":"10"}]'},
        ),
        (None, {}),
    ],
)
def test_format_search_filters_for_remote(raw, formatted):
    assert request_formatter.format_search_filters_for_remote(raw) == formatted


@pytest.mark.parametrize(
    "ordering, ascending, formatted",
    [
        ("creation_date", False, "-creation_date"),
        ("start_date", True, "start_date"),
    ],
)
def test_format_search_ordering_for_remote(ordering, ascending, formatted):
    assert request_formatter.format_search_ordering_for_remote(ordering, ascending) == formatted
