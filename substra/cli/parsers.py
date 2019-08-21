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


class BaseFieldParser:
    def __init__(self, field_name, field_ref):
        self.field_name = field_name
        self.field_ref = field_ref

    def _print(self, name, value, field_length):
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

    def print(self, item, field_length):
        name = self.field_name.upper().ljust(field_length)
        value = find_dict_composite_key_value(item, self.field_ref)
        self._print(name, value, field_length)


class PermissionsFieldParser(BaseFieldParser):
    def _print(self, name, value, field_length):
        value = 'owner only' if value == [] else value
        super()._print(name, value, field_length)


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
        field_items = (('Key', self.key_field),) + self.many_fields
        for field_name, field_ref in field_items:
            values = [
                str(find_dict_composite_key_value(item, field_ref))
                for item in items
            ]

            column = [field_name.upper()]
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

    def _get_single_fields_parsers(self):
        return [BaseFieldParser('key', self.key_field)] + [
            field_parser if isinstance(field_parser, BaseFieldParser)
            else BaseFieldParser(*field_parser)
            for field_parser in self.single_fields]

    def _get_asset_field_length(self):
        fields = [parser.field_name for parser in self._get_single_fields_parsers()]
        max_field_length = max([len(x) for x in fields])
        field_length = (math.ceil(max_field_length / 4) + 1) * 4
        return field_length

    def print_single(self, item, raw):
        """Display single item."""

        if raw:
            print(json.dumps(item, indent=2))
            return

        field_length = self._get_asset_field_length()
        for field_parser in self._get_single_fields_parsers():
            field_parser.print(item, field_length)

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
        ('Name', 'name'),
    )
    single_fields = (
        ('Name', 'name'),
        PermissionsFieldParser('Processable by', 'permissions.process'),
        PermissionsFieldParser('Downloadable by', 'permissions.download'),
    )

    download_message = 'Download this algorithm\'s code:'


class ObjectiveParser(BaseAssetParser):
    asset_name = 'objective'

    many_fields = (
        ('Name', 'name'),
        ('Metrics', 'metrics.name'),
    )
    single_fields = (
        ('Name', 'name'),
        ('Metrics', 'metrics.name'),
        ('Test dataset key', 'testDataset.dataManagerKey'),
        ('Test data sample keys', 'testDataset.dataSampleKeys'),
        PermissionsFieldParser('Processable by', 'permissions.process'),
        PermissionsFieldParser('Downloadable by', 'permissions.download'),
    )
    download_message = 'Download this objective\'s metric:'


class DataSampleParser(BaseAssetParser):
    asset_name = 'data sample'


class DatasetParser(BaseAssetParser):
    asset_name = 'dataset'

    many_fields = (
        ('Name', 'name'),
        ('Type', 'type'),
    )
    single_fields = (
        ('Name', 'name'),
        ('Objective key', 'objectiveKey'),
        ('Type', 'type'),
        ('Train data sample keys', 'trainDataSampleKeys'),
        ('Test data sample keys', 'testDataSampleKeys'),
        PermissionsFieldParser('Processable by', 'permissions.process'),
        PermissionsFieldParser('Downloadable by', 'permissions.download'),
    )
    download_message = 'Download this data manager\'s opener:'


class TraintupleParser(BaseAssetParser):
    asset_name = 'traintuple'

    many_fields = (
        ('Algo name', 'algo.name'),
        ('Status', 'status'),
        ('Perf', 'dataset.perf'),
    )
    single_fields = (
        ('Model key', 'outModel.hash'),
        ('Algo key', 'algo.hash'),
        ('Algo name', 'algo.name'),
        ('Objective key', 'objective.hash'),
        ('Status', 'status'),
        ('Perf', 'dataset.perf'),
        ('Train data sample keys', 'dataset.keys'),
        ('Rank', 'rank'),
        ('Compute Plan Id', 'computePlanID'),
        ('Tag', 'tag'),
        ('Log', 'log'),
        PermissionsFieldParser('Processable by', 'permissions.process'),
        PermissionsFieldParser('Downloadable by', 'permissions.download'),
    )
    has_description = False


class TesttupleParser(BaseAssetParser):
    asset_name = 'testtuple'

    many_fields = (
        ('Algo name', 'algo.name'),
        ('Certified', 'certified'),
        ('Status', 'status'),
        ('Perf', 'dataset.perf')
    )
    single_fields = (
        ('Traintuple key', 'model.traintupleKey'),
        ('Algo key', 'algo.hash'),
        ('Algo name', 'algo.name'),
        ('Objective key', 'objective.hash'),
        ('Certified', 'certified'),
        ('Status', 'status'),
        ('Perf', 'dataset.perf'),
        ('Test data sample keys', 'dataset.keys'),
        ('Tag', 'tag'),
        ('Log', 'log'),
        PermissionsFieldParser('Processable by', 'permissions.process'),
        PermissionsFieldParser('Downloadable by', 'permissions.download'),
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
