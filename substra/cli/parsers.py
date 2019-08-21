import json
import math

from substra.sdk import assets


def find_dict_composite_key_value(asset_dict, composite_key):
    def _recursive_find(d, keys):
        value = d.get(keys[0])
        if len(keys) == 1:
            return value
        return _recursive_find(value or {}, keys[1:])

    return _recursive_find(asset_dict, composite_key.split('.'))


class Field:
    def __init__(self, field_name, field_ref):
        self.field_name = field_name
        self.field_ref = field_ref

    def print_single_name_value(self, name, value, field_length):
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
                print(f'{name} None')
        else:
            print(f'{name}{value}')

    def get_value(self, item):
        return find_dict_composite_key_value(item, self.field_ref)

    def print_single(self, item, field_length):
        name = self.field_name.upper().ljust(field_length)
        value = self.get_value(item)
        self.print_single_name_value(name, value, field_length)


class PermissionField(Field):
    def print_single_name_value(self, name, value, field_length):
        value = 'owner only' if value == [] else value
        super().print_single_name_value(name, value, field_length)


class BaseAssetParser:
    asset_name = None

    key_field = 'key'
    many_fields = ()
    single_fields = ()

    download_message = None
    has_description = True

    def print_list(self, items, raw):
        """Display many items."""

        if raw:
            print(json.dumps(items, indent=2))
            return

        columns = []
        for field in self._get_many_fields():
            values = [
                str(field.get_value(item))
                for item in items
            ]

            column = [field.field_name.upper()]
            column.extend(values)

            columns.append(column)

        column_widths = []
        for column in columns:
            width = max([len(x) for x in column])
            width = (math.ceil(width / 4) + 1) * 4
            column_widths.append(width)

        for row_index in range(len(items) + 1):
            for col_index, column in enumerate(columns):
                print(column[row_index].ljust(column_widths[col_index]), end='')
            print()

    def _get_many_fields(self):
        return (Field('key', self.key_field), ) + self.many_fields

    def _get_single_fields(self):
        return (Field('key', self.key_field), ) + self.single_fields

    def _get_asset_field_length(self):
        fields = [field.field_name for field in self._get_single_fields()]
        max_field_length = max([len(x) for x in fields])
        field_length = (math.ceil(max_field_length / 4) + 1) * 4
        return field_length

    def print_single(self, item, raw):
        """Display single item."""

        if raw:
            print(json.dumps(item, indent=2))
            return

        field_length = self._get_asset_field_length()
        for field in self._get_single_fields():
            field.print_single(item, field_length)

        key_value = find_dict_composite_key_value(item, self.key_field)

        if self.download_message:
            print()
            print(self.download_message)
            print(f'\tsubstra download {self.asset_name} {key_value}')

        if self.has_description:
            print()
            print('Display this asset description:')
            print(f'\tsubstra describe {self.asset_name} {key_value}')


class JsonOnlyParser:
    @staticmethod
    def _print(data):
        print(json.dumps(data, indent=2))

    def print_list(self, items, raw):
        self._print(items)

    def print_single(self, item, raw):
        self._print(item)


class AlgoParser(BaseAssetParser):
    asset_name = 'algo'

    many_fields = (
        Field('Name', 'name'),
    )
    single_fields = (
        Field('Name', 'name'),
        PermissionField('Processable by', 'permissions.process'),
        PermissionField('Downloadable by', 'permissions.download'),
    )

    download_message = 'Download this algorithm\'s code:'


class ObjectiveParser(BaseAssetParser):
    asset_name = 'objective'

    many_fields = (
        Field('Name', 'name'),
        Field('Metrics', 'metrics.name'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Metrics', 'metrics.name'),
        Field('Test dataset key', 'testDataset.dataManagerKey'),
        Field('Test data sample keys', 'testDataset.dataSampleKeys'),
        PermissionField('Processable by', 'permissions.process'),
        PermissionField('Downloadable by', 'permissions.download'),
    )
    download_message = 'Download this objective\'s metric:'


class DataSampleParser(BaseAssetParser):
    asset_name = 'data sample'


class DatasetParser(BaseAssetParser):
    asset_name = 'dataset'

    many_fields = (
        Field('Name', 'name'),
        Field('Type', 'type'),
    )
    single_fields = (
        Field('Name', 'name'),
        Field('Objective key', 'objectiveKey'),
        Field('Type', 'type'),
        Field('Train data sample keys', 'trainDataSampleKeys'),
        Field('Test data sample keys', 'testDataSampleKeys'),
        PermissionField('Processable by', 'permissions.process'),
        PermissionField('Downloadable by', 'permissions.download'),
    )
    download_message = 'Download this data manager\'s opener:'


class TraintupleParser(BaseAssetParser):
    asset_name = 'traintuple'

    many_fields = (
        Field('Algo name', 'algo.name'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
    )
    single_fields = (
        Field('Model key', 'outModel.hash'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Objective key', 'objective.hash'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Train data sample keys', 'dataset.keys'),
        Field('Rank', 'rank'),
        Field('Compute Plan Id', 'computePlanID'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        PermissionField('Processable by', 'permissions.process'),
        PermissionField('Downloadable by', 'permissions.download'),
    )
    has_description = False


class TesttupleParser(BaseAssetParser):
    asset_name = 'testtuple'

    many_fields = (
        Field('Algo name', 'algo.name'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf')
    )
    single_fields = (
        Field('Traintuple key', 'model.traintupleKey'),
        Field('Algo key', 'algo.hash'),
        Field('Algo name', 'algo.name'),
        Field('Objective key', 'objective.hash'),
        Field('Certified', 'certified'),
        Field('Status', 'status'),
        Field('Perf', 'dataset.perf'),
        Field('Test data sample keys', 'dataset.keys'),
        Field('Tag', 'tag'),
        Field('Log', 'log'),
        PermissionField('Processable by', 'permissions.process'),
        PermissionField('Downloadable by', 'permissions.download'),
    )
    has_description = False


PARSERS = {
    assets.ALGO: AlgoParser,
    assets.OBJECTIVE: ObjectiveParser,
    assets.DATASET: DatasetParser,
    assets.DATA_SAMPLE: DataSampleParser,
    assets.TRAINTUPLE: TraintupleParser,
    assets.TESTTUPLE: TesttupleParser,
}


def get_parser(asset):
    return PARSERS[asset]() if asset in PARSERS else JsonOnlyParser()
