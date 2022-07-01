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


@pytest.mark.parametrize(
    "asset,output_format,printer_cls",
    [
        ("compute_plan", "pretty", printers.AssetPrinter),
        ("compute_plan", "json", printers.JsonPrinter),
        ("compute_plan", "yaml", printers.YamlPrinter),
        ("foo", "pretty", printers.JsonPrinter),
        ("foo", "json", printers.JsonPrinter),
        ("foo", "yaml", printers.YamlPrinter),
    ],
)
def test_get_asset_printer(asset, output_format, printer_cls):
    assert isinstance(printers.get_asset_printer(asset, output_format), printer_cls)
