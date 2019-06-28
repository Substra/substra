import json
import math

from substra import assets


def find_dict_composite_key_value(asset_dict, composite_key):
    def _recursive_find(o, keys):
        value = o.get(keys[0])
        if len(keys) == 1:
            return value
        return _recursive_find(value or {}, keys[1:])

    return _recursive_find(asset_dict, composite_key.split('.'))


class BaseParser:
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

    def _get_asset_field_length(self):
        fields = ['key'] + [field for field, _ in self.single_fields]
        max_field_length = max([len(x) for x in fields])
        field_length = (math.ceil(max_field_length / 4) + 1) * 4
        return field_length

    def _print_single_fields(self, item, field_length):
        field_items = (('key', self.key_field), ) + self.single_fields
        for field_name, field_ref in field_items:
            name = field_name.upper().ljust(field_length)
            value = find_dict_composite_key_value(item, field_ref)
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

    def print_single(self, item, raw):
        """Display single item."""

        if raw:
            print(json.dumps(item, indent=2))
            return

        field_length = self._get_asset_field_length()
        self._print_single_fields(item, field_length)

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


class AlgoParser(BaseParser):
    asset_name = 'algo'

    many_fields = (
        ('Name', 'name'),
    )
    single_fields = (
        ('Name', 'name'),
    )

    download_message = 'Download this algorithm\'s code:'


class ObjectiveParser(BaseParser):
    asset_name = 'objective'

    many_fields = (
        ('Name', 'name'),
        ('Metrics', 'metrics.name'),
    )
    single_fields = (
        ('Name', 'name'),
        ('Metrics', 'metrics.name'),
        ('Test dataset', 'testDataset.dataManagerKey'),
        ('Test data samples', 'testDataset.dataSampleKeys'),
    )
    download_message = 'Download this objective\'s metric:'


class DatasetParser(BaseParser):
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
    )
    download_message = 'Download this data manager\'s opener:'


class TraintupleParser(BaseParser):
    asset_name = 'traintuple'

    many_fields = (
        ('Algo name', 'algo.name'),
        ('Status', 'status'),
        ('Score', 'dataset.perf'),
    )
    single_fields = (
        ('Model key', 'outModel.hash'),
        ('Algo key', 'algo.hash'),
        ('Algo name', 'algo.name'),
        ('Objective key', 'objective.hash'),
        ('Status', 'status'),
        ('Score', 'dataset.perf'),
        ('Train data sample keys', 'dataset.keys'),
        ('Rank', 'rank'),
        ('FL Task', 'fltask'),
        ('Tag', 'tag'),
    )
    has_description = False


class TesttupleParser(BaseParser):
    asset_name = 'testtuple'

    many_fields = (
        ('Algo name', 'algo.name'),
        ('Certified', 'certified'),
        ('Status', 'status'),
        ('Score', 'dataset.perf')
    )
    single_fields = (
        ('Traintuple key', 'model.traintupleKey'),
        ('Algo key', 'algo.hash'),
        ('Algo name', 'algo.name'),
        ('Objective key', 'objective.hash'),
        ('Certified', 'certified'),
        ('Status', 'status'),
        ('Score', 'dataset.perf'),
        ('Test data sample keys', 'dataset.keys'),
        ('Tag', 'tag'),
    )
    has_description = False


PARSERS = {
    assets.ALGO: AlgoParser,
    assets.OBJECTIVE: ObjectiveParser,
    assets.DATASET: DatasetParser,
    assets.TRAINTUPLE: TraintupleParser,
    assets.TESTTUPLE: TesttupleParser,
}


def get_parser(asset):
    return PARSERS[asset]() if asset in PARSERS else JsonOnlyParser()
