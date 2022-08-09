import enum
import json
import math

import pydantic
import yaml


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
