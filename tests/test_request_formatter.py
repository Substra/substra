# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
        ("creation_date", False, "creation_date"),
        ("start_date", True, "-start_date"),
    ],
)
def test_format_search_ordering_for_remote(ordering, ascending, formatted):
    assert request_formatter.format_search_ordering_for_remote(ordering, ascending) == formatted
