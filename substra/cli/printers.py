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


class CountField(Field):
    def get_value(self, item, **kwargs):
        value = super().get_value(item)
        if value:
            return len(value)
        return 0


class InModelTraintupleKeysField(KeysField):
    def _get_key(self, v):
        return v.get('traintupleKey')


class CurrentNodeField(Field):
    def get_value(self, item, expand=False):
        value = super().get_value(item, expand)
        if value:
            return '(current)'
        return ''


class ProgressField(Field):
    def __init__(self, name, progress_ref, total_ref):
        self.name = name
        self.progress_ref = progress_ref
        self.total_ref = total_ref

    def get_value(self, item, expand=False):
        done_count = find_dict_composite_key_value(item, self.progress_ref)
        tuple_count = find_dict_composite_key_value(item, self.total_ref)
        return f'{done_count}/{tuple_count}'


class MappingField(Field):
    def get_value(self, item, expand=False):
        mapping = super().get_value(item) or {}
        if expand:
            value = [f'{k}:{v}' for k, v in mapping.items()]
        else:
            value = f'{len(mapping)} values'
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

    def get_profile_arg(self, profile):
        if profile and profile != 'default':
            return f'--profile {profile}'
        return ''

    def print_download_message(self, item, profile=None):
        if self.download_message:
            key_value = self.key_field.get_value(item)
            profile_arg = self.get_profile_arg(profile)
            print('\n' + self.download_message)
            print(f'\tsubstra download {self.asset_name} {key_value} {profile_arg}')

    def print_description_message(self, item, profile=None):
        if self.has_description:
            key_value = self.key_field.get_value(item)
            profile_arg = self.get_profile_arg(profile)
            print(f'\nDisplay this {self.asset_name}\'s description:')
            print(f'\tsubstra describe {self.asset_name} {key_value} {profile_arg}')

    def print_messages(self, item, profile=None):
        self.print_download_message(item, profile)
        self.print_description_message(item, profile)

    def print(self, data, profile=None, expand=False, is_list=False):
        if is_list:
            self.print_table(data, self._get_list_fields())
        else:
            self.print_details(data, self._get_single_fields(), expand)
            self.print_messages(data, profile)


class JsonPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        print(json.dumps(data, indent=2))


class YamlPrinter:
    @staticmethod
    def print(data, *args, **kwargs):
        print(yaml.dump(data, default_flow_style=False))


class BaseAlgoPrinter(AssetPrinter):
    list_fields = (
        Field('Name', 'name'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Owner', 'owner'),
        PermissionField('Permissions', 'permissions'),
    )

    download_message = 'Download this algorithm\'s code:'


class ComputePlanPrinter(AssetPrinter):
    asset_name = 'compute_plan'

    key_field = Field('Compute plan ID', 'computePlanID')

    list_fields = (
        CountField('Traintuples count', 'traintupleKeys'),
        CountField('Composite traintuples count', 'compositeTraintupleKeys'),
        CountField('Aggregatetuples count', 'aggregatetupleKeys'),
        CountField('Testtuples count', 'testtupleKeys'),
        ProgressField('Progress', 'doneCount', 'tupleCount'),
        Field('Status', 'status'),
        Field('Tag', 'tag'),
        Field('Clean model', 'clean_model'),
    )
    single_fields = (
        KeysField('Traintuple keys', 'traintupleKeys'),
        KeysField('Composite traintuple keys', 'compositeTraintupleKeys'),
        KeysField('Aggregatetuple keys', 'aggregatetupleKeys'),
        KeysField('Testtuple keys', 'testtupleKeys'),
        ProgressField('Progress', 'doneCount', 'tupleCount'),
        Field('Status', 'status'),
        Field('Tag', 'tag'),
        Field('Clean model', 'clean_model'),
        MappingField('ID to key mapping', 'IDToKey'),
    )

    def print_messages(self, item, profile=None):
        key_value = self.key_field.get_value(item)
        profile_arg = self.get_profile_arg(profile)

        print('\nDisplay this compute_plan\'s traintuples:')
        print(f'\tsubstra list traintuple -f "traintuple:computePlanID:{key_value}" {profile_arg}')

        print('\nDisplay this compute_plan\'s composite_traintuples:')
        print(f'\tsubstra list composite_traintuple'
              f' -f "composite_traintuple:computePlanID:{key_value}" {profile_arg}')

        print('\nDisplay this compute_plan\'s aggregatetuples:')
        print(f'\tsubstra list aggregatetuple'
              f' -f "aggregatetuple:computePlanID:{key_value}" {profile_arg}')

        print('\nDisplay this compute_plan\'s testtuples:')
        print(f'\tsubstra list testtuple'
              f' -f "testtuple:computePlanID:{key_value}" {profile_arg}')


class AlgoPrinter(BaseAlgoPrinter):
    asset_name = 'algo'


class AggregateAlgoPrinter(BaseAlgoPrinter):
    asset_name = 'aggregate_algo'


class CompositeAlgoPrinter(BaseAlgoPrinter):
    asset_name = 'composite_algo'


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

    def print_leaderboard_message(self, item, profile=None):
        key_value = self.key_field.get_value(item)
        profile_arg = self.get_profile_arg(profile)
        print('\nDisplay this objective\'s leaderboard:')
        print(f'\tsubstra leaderboard {key_value} {profile_arg}')

    def print_messages(self, item, profile=None):
        super().print_messages(item, profile)
        self.print_leaderboard_message(item, profile)


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
        Field('Rank', 'rank'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
    )
    single_fields = (
        Field('Model key', 'outModel.hash'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Status', 'status'),
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

    def print_messages(self, item, profile=None):
        key_value = self.key_field.get_value(item)
        profile_arg = self.get_profile_arg(profile)

        print('\nDisplay this traintuple\'s testtuples:')
        print(f'\tsubstra list testtuple -f "testtuple:traintupleKey:{key_value}" {profile_arg}')


class AggregateTuplePrinter(AssetPrinter):
    asset_name = 'aggregatetuple'

    list_fields = (
        Field('Algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Rank', 'rank'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
    )
    single_fields = (
        Field('Model key', 'outModel.hash'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Dataset key', 'dataset.openerHash'),
        InModelTraintupleKeysField('In model keys', 'inModels'),
        Field('Rank', 'rank'),
        Field('Compute Plan Id', 'computePlanID'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        Field('Creator', 'creator'),
        Field('Worker', 'dataset.worker'),
        PermissionField('Permissions', 'permissions'),
    )
    has_description = False

    def print_messages(self, item, profile=None):
        key_value = self.key_field.get_value(item)
        profile_arg = self.get_profile_arg(profile)

        print('\nDisplay this aggregatetuple\'s testtuples:')
        print(f'\tsubstra list testtuple -f "testtuple:traintupleKey:{key_value}" {profile_arg}')


class CompositeTraintuplePrinter(AssetPrinter):
    asset_name = 'composite_traintuple'

    list_fields = (
        Field('Composite algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Rank', 'rank'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
    )

    single_fields = (
        Field('Out head model key', 'outHeadModel.outModel.hash'),
        PermissionField('Out head model permissions', 'outHeadModel.permissions'),
        Field('Out trunk model key', 'outTrunkModel.outModel.hash'),
        PermissionField('Out trunk model permissions', 'outTrunkModel.permissions'),
        Field('Composite algo key', 'algo.hash'),
        Field('Composite algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Dataset key', 'dataset.openerHash'),
        KeysField('Train data sample keys', 'dataset.keys'),
        Field('In head model key', 'inHeadModel.traintupleKey'),
        Field('In trunk model key', 'inTrunkModel.traintupleKey'),
        Field('Rank', 'rank'),
        Field('Compute Plan Id', 'computePlanID'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        Field('Creator', 'creator'),
        Field('Worker', 'dataset.worker'),
    )
    has_description = False

    def print_messages(self, item, profile=None):
        key_value = self.key_field.get_value(item)
        profile_arg = self.get_profile_arg(profile)

        print('\nDisplay this composite traintuple\'s testtuples:')
        print(f'\tsubstra list testtuple -f "testtuple:traintupleKey:{key_value}" {profile_arg}')


class TesttuplePrinter(AssetPrinter):
    asset_name = 'testtuple'

    list_fields = (
        Field('Algo name', 'algo.name'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Rank', 'rank'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
    )
    single_fields = (
        Field('Traintuple key', 'traintupleKey'),
        Field('Traintuple type', 'traintupleType'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Objective key', 'objective.hash'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Dataset key', 'dataset.openerHash'),
        KeysField('Test data sample keys', 'dataset.keys'),
        Field('Rank', 'rank'),
        Field('Tag', 'tag'),
        Field('Compute Plan Id', 'computePlanID'),
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
        Field('Traintuple key', 'traintupleKey'),
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
    assets.COMPUTE_PLAN: ComputePlanPrinter,
    assets.AGGREGATE_ALGO: AggregateAlgoPrinter,
    assets.COMPOSITE_ALGO: CompositeAlgoPrinter,
    assets.OBJECTIVE: ObjectivePrinter,
    assets.DATASET: DatasetPrinter,
    assets.DATA_SAMPLE: DataSamplePrinter,
    assets.TRAINTUPLE: TraintuplePrinter,
    assets.AGGREGATETUPLE: AggregateTuplePrinter,
    assets.COMPOSITE_TRAINTUPLE: CompositeTraintuplePrinter,
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
