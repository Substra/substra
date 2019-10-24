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

import json
import math

import yaml

from substra.sdk import assets


def find_dict_composite_key_value(asset_dict, composite_key):
    def _recursive_find(d, keys):
        value = d.get(keys[0])
        if len(keys) == 1:
            return value
        return _recursive_find(value or {}, keys[1:])

    return _recursive_find(asset_dict, composite_key.split('.'))


class Field:
    def __init__(self, name, ref):
        self.name = name
        self.ref = ref

    def get_value(self, item, expand=False):
        return find_dict_composite_key_value(item, self.ref)

    def print_details(self, item, field_length, expand):
        name = self.name.upper().ljust(field_length)
        value = self.get_value(item, expand)

        if isinstance(value, list):
            if value:
                print(name, end='')
                padding = ' ' * field_length
                for i, v in enumerate(value):
                    if i == 0:
                        print(f'- {v}')
                    else:
                        print(f'{padding}- {v}')
            else:
                print(f'{name}None')
        else:
            print(f'{name}{value}')


class PermissionField(Field):
    def get_value(self, item, expand=False):
        is_public = find_dict_composite_key_value(item, f'{self.ref}.process.public')
        if is_public:
            return 'Processable by anyone'

        authorized_ids = find_dict_composite_key_value(item, f'{self.ref}.process.authorizedIDs')
        if not authorized_ids:
            return 'Processable by its owner only'

        return authorized_ids

    def print_details(self, item, field_length, expand):
        value = self.get_value(item, expand)
        if isinstance(value, list):
            name = self.name.upper().ljust(field_length)
            padding = ' ' * field_length
            print(f'{name}Processable by:')
            for v in value:
                print(f'{padding}- {v}')
        else:
            super().print_details(item, field_length, expand)


class KeysField(Field):
    def _get_key(self, v):
        return v

    def get_value(self, item, expand=False):
        value = super().get_value(item, expand)
        if not expand and value:
            n = len(value)
            value = f'{n} key' if n == 1 else f'{n} keys'
        elif value:
            value = [self._get_key(v) for v in value]
        return value


class InModelTraintupleKeysField(KeysField):
    def _get_key(self, v):
        return v.get('traintupleKey')


class CurrentNodeField(Field):
    def get_value(self, item, expand=False):
        value = super().get_value(item, expand)
        if value:
            return '(current)'
        return ''


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
                print(column[row_index].ljust(column_widths[col_index]), end='')
            print()

    @staticmethod
    def _get_field_name_length(fields):
        max_length = max([len(field.name) for field in fields])
        length = (math.ceil(max_length / 4) + 1) * 4
        return length

    def print_details(self, item, fields, expand):
        field_length = self._get_field_name_length(fields)
        for field in fields:
            field.print_details(item, field_length, expand)


class AssetPrinter(BasePrinter):
    asset_name = None

    key_field = Field('key', 'key')
    list_fields = ()
    single_fields = ()

    download_message = None
    has_description = True

    def _get_list_fields(self):
        return (self.key_field, ) + self.list_fields

    def _get_single_fields(self):
        return (self.key_field, ) + self.single_fields

    def print_download_message(self, item):
        if self.download_message:
            key_value = self.key_field.get_value(item)
            print()
            print(self.download_message)
            print(f'\tsubstra download {self.asset_name} {key_value}')

    def print_description_message(self, item):
        if self.has_description:
            key_value = self.key_field.get_value(item)
            print()
            print(f'Display this {self.asset_name}\'s description:')
            print(f'\tsubstra describe {self.asset_name} {key_value}')

    def print_messages(self, item):
        self.print_download_message(item)
        self.print_description_message(item)

    def print(self, data, expand=False, is_list=False):
        if is_list:
            self.print_table(data, self._get_list_fields())
        else:
            self.print_details(data, self._get_single_fields(), expand)
            self.print_messages(data)


class JsonPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        print(json.dumps(data, indent=2))


class YamlPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        print(yaml.dump(data, default_flow_style=False))


class AlgoPrinter(AssetPrinter):
    asset_name = 'algo'

    list_fields = (
        Field('Name', 'name'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Owner', 'owner'),
        PermissionField('Permissions', 'permissions'),
    )

    download_message = 'Download this algorithm\'s code:'


class ObjectivePrinter(AssetPrinter):
    asset_name = 'objective'

    list_fields = (
        Field('Name', 'name'),
        Field('Metrics', 'metrics.name'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Metrics', 'metrics.name'),
        Field('Test dataset key', 'testDataset.dataManagerKey'),
        KeysField('Test data sample keys', 'testDataset.dataSampleKeys'),
        Field('Owner', 'owner'),
        PermissionField('Permissions', 'permissions'),
    )
    download_message = 'Download this objective\'s metric:'

    def print_leaderboard_message(self, item):
        key_value = self.key_field.get_value(item)
        print()
        print('Display this objective\'s leaderboard:')
        print(f'\tsubstra leaderboard {key_value}')

    def print_messages(self, item):
        super().print_messages(item)
        self.print_leaderboard_message(item)


class DataSamplePrinter(AssetPrinter):
    asset_name = 'data sample'


class DatasetPrinter(AssetPrinter):
    asset_name = 'dataset'

    list_fields = (
        Field('Name', 'name'),
        Field('Type', 'type'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Objective key', 'objectiveKey'),
        Field('Type', 'type'),
        KeysField('Train data sample keys', 'trainDataSampleKeys'),
        KeysField('Test data sample keys', 'testDataSampleKeys'),
        Field('Owner', 'owner'),
        PermissionField('Permissions', 'permissions'),
    )
    download_message = 'Download this data manager\'s opener:'


class TraintuplePrinter(AssetPrinter):
    asset_name = 'traintuple'

    list_fields = (
        Field('Algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
    )
    single_fields = (
        Field('Model key', 'outModel.hash'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Objective key', 'objective.hash'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Dataset key', 'dataset.openerHash'),
        KeysField('Train data sample keys', 'dataset.keys'),
        InModelTraintupleKeysField('In model traintuple keys', 'inModels'),
        Field('Rank', 'rank'),
        Field('Compute Plan Id', 'computePlanID'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        Field('Creator', 'creator'),
        Field('Worker', 'dataset.worker'),
        PermissionField('Permissions', 'permissions'),
    )
    has_description = False


class TesttuplePrinter(AssetPrinter):
    asset_name = 'testtuple'

    list_fields = (
        Field('Algo name', 'algo.name'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Tag', 'tag'),
    )
    single_fields = (
        Field('Traintuple key', 'model.traintupleKey'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Objective key', 'objective.hash'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Dataset key', 'dataset.openerHash'),
        KeysField('Test data sample keys', 'dataset.keys'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        Field('Creator', 'creator'),
        Field('Worker', 'dataset.worker'),
        PermissionField('Permissions', 'permissions'),
    )
    has_description = False


class NodePrinter(AssetPrinter):
    asset_name = 'node'
    key_field = Field('NODE ID', 'id')
    list_fields = (
        CurrentNodeField('', 'isCurrent'),
    )


class LeaderBoardPrinter(BasePrinter):
    objective_fields = (Field('Key', 'key'), ) + ObjectivePrinter.single_fields
    testtuple_fields = (
        Field('Perf', 'perf'),
        Field('Algo name', 'algo.name'),
        Field('Traintuple key', 'model.traintupleKey'),
    )

    def print(self, leaderboard, expand):
        objective = leaderboard['objective']
        testtuples = leaderboard['testtuples']

        print('========== OBJECTIVE ==========')
        self.print_details(objective, self.objective_fields, expand)
        print()
        print('========= LEADERBOARD =========')
        self.print_table(testtuples, self.testtuple_fields)


PRINTERS = {
    assets.ALGO: AlgoPrinter,
    assets.OBJECTIVE: ObjectivePrinter,
    assets.DATASET: DatasetPrinter,
    assets.DATA_SAMPLE: DataSamplePrinter,
    assets.TRAINTUPLE: TraintuplePrinter,
    assets.TESTTUPLE: TesttuplePrinter,
    assets.NODE: NodePrinter,
}


def get_asset_printer(asset, output_format):
    if output_format == 'pretty' and asset in PRINTERS:
        return PRINTERS[asset]()

    if output_format == 'yaml':
        return YamlPrinter()

    return JsonPrinter()


def get_leaderboard_printer(output_format):
    if output_format == 'pretty':
        return LeaderBoardPrinter()

    if output_format == 'yaml':
        return YamlPrinter()

    return JsonPrinter()
