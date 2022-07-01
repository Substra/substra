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

import enum
import json
import math

import pydantic
import yaml

from substra.sdk import assets


def find_dict_composite_key_value(asset_dict, composite_key):
    def _recursive_find(d, keys):
        value = d.get(keys[0])
        if len(keys) == 1:
            return value
        return _recursive_find(value or {}, keys[1:])

    return _recursive_find(asset_dict, composite_key.split("."))


class Field:
    def __init__(self, name, ref):
        self.name = name
        self.ref = ref

    def get_value(self, item, expand=False):
        value = find_dict_composite_key_value(item, self.ref)
        if isinstance(value, enum.Enum):
            value = value.name
        return value

    def print_details(self, item, field_length, expand):
        name = self.name.upper().ljust(field_length)
        value = self.get_value(item, expand)
        if isinstance(value, dict):
            value = [f"{k}: {v}" for k, v in value.items()]
        if isinstance(value, list):
            if value:
                print(name, end="")
                padding = " " * field_length
                for i, v in enumerate(value):
                    if i == 0:
                        print(f"- {v}")
                    else:
                        print(f"{padding}- {v}")
            else:
                print(f"{name}None")
        else:
            print(f"{name}{value}")


class ProgressField(Field):
    def __init__(self, name, progress_ref, total_ref):
        self.name = name
        self.progress_ref = progress_ref
        self.total_ref = total_ref

    def get_value(self, item, expand=False):
        done_count = find_dict_composite_key_value(item, self.progress_ref)
        tuple_count = find_dict_composite_key_value(item, self.total_ref)
        return f"{done_count}/{tuple_count}"


class MappingField(Field):
    def get_value(self, item, expand=False):
        mapping = super().get_value(item) or {}
        if expand:
            value = [f"{k}:{v}" for k, v in mapping.items()]
        else:
            value = f"{len(mapping)} values"
        return value


class BasePrinter:
    @staticmethod
    def _get_columns(items, fields):
        columns = []
        for field in fields:
            values = [str(field.get_value(item)) for item in items]

            column = [field.name.upper()]
            column.extend(values)

            columns.append(column)
        return columns

    @staticmethod
    def _get_column_widths(columns):
        column_widths = []
        for column in columns:
            width = max([len(x) for x in column])
            width = (math.ceil(width / 4) + 1) * 4
            column_widths.append(width)
        return column_widths

    def print_table(self, items, fields):
        columns = self._get_columns(items, fields)
        column_widths = self._get_column_widths(columns)

        for row_index in range(len(items) + 1):
            for col_index, column in enumerate(columns):
                print(column[row_index].ljust(column_widths[col_index]), end="")
            print()

    @staticmethod
    def _get_field_name_length(fields):
        max_length = max([len(field.name) for field in fields])
        length = (math.ceil(max_length / 4) + 1) * 4
        return length

    def print_details(self, item, fields, expand):
        if isinstance(item, pydantic.BaseModel):
            item = item.dict(exclude_none=False, by_alias=True)
        field_length = self._get_field_name_length(fields)
        for field in fields:
            field.print_details(item, field_length, expand)


class AssetPrinter(BasePrinter):
    asset_type = None

    key_field = Field("key", "key")
    list_fields = ()
    single_fields = ()

    has_description = True

    def _get_list_fields(self):
        return (self.key_field,) + self.list_fields

    def _get_single_fields(self):
        return (self.key_field,) + self.single_fields

    def get_profile_arg(self, profile):
        if profile and profile != "default":
            return f"--profile {profile}"
        return ""

    def print_description_message(self, item, profile=None):
        if self.has_description:
            key_value = self.key_field.get_value(item)
            profile_arg = self.get_profile_arg(profile)
            print(f"\nDisplay this {self.asset_type}'s description:")
            print(f"\tsubstra describe {self.asset_type} {key_value} {profile_arg}")

    def print_messages(self, item, profile=None):
        self.print_description_message(item, profile)

    def print(self, data, profile=None, expand=False, is_list=False):
        if isinstance(data, pydantic.BaseModel):
            data = data.dict(exclude_none=False, by_alias=True)
        if is_list:
            self.print_table(data, self._get_list_fields())
        else:
            self.print_details(data, self._get_single_fields(), expand)
            self.print_messages(data, profile)


class JsonPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        if isinstance(data, pydantic.BaseModel):
            data = data.dict()
        print(json.dumps(data, indent=2, default=str))


class YamlPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        # We need the yaml format to display the same things than json format
        if isinstance(data, pydantic.BaseModel):
            data = data.dict()
        json_format = json.dumps(data, indent=2, default=str)
        print(yaml.dump(json.loads(json_format), default_flow_style=False))


class OrganizationInfoPrinter(BasePrinter):
    single_fields = (
        Field("Host", "host"),
        Field("Channel", "channel"),
        Field("Backend version", "version"),
        Field("Orchestrator version", "orchestrator_version"),
        Field("Chaincode version", "chaincode_version"),
        MappingField("Config", "config"),
    )

    def print(self, data):
        self.print_details(data, self.single_fields, expand=True)


class ComputePlanPrinter(AssetPrinter):
    asset_type = "compute_plan"

    list_fields = (
        ProgressField("Progress", "done_count", "task_count"),
        Field("Status", "status"),
        Field("Tag", "tag"),
        Field("Clean model", "delete_intermediary_models"),
    )
    single_fields = (
        Field("Done count", "done_count"),
        Field("Task count", "task_count"),
        ProgressField("Progress", "done_count", "task_count"),
        Field("Failed task", "failed_task.key"),
        Field("Failed task category", "failed_task.category"),
        Field("Status", "status"),
        Field("Tag", "tag"),
        Field("Name", "name"),
        Field("Metadata", "metadata"),
        Field("Clean model", "delete_intermediary_models"),
    )


PRINTERS = {
    assets.COMPUTE_PLAN: ComputePlanPrinter,
}


def get_asset_printer(asset, output_format):
    if output_format == "pretty" and asset in PRINTERS:
        return PRINTERS[asset]()

    if output_format == "yaml":
        return YamlPrinter()

    return JsonPrinter()
