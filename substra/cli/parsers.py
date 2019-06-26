import json
import math
import textwrap
from functools import wraps
from substra import assets


def get_recursive(obj, key):
    def _inner(o, keys):
        k, *keys = keys
        if keys:
            return _inner(o.get(k) or {}, keys)
        return o.get(k, None)

    return _inner(obj, key.split('.'))


def get_prop_value(obj, key):
    if callable(key):
        return key(obj)
    return get_recursive(obj, key)


def handle_raw_option(method):
    @wraps(method)
    def print_raw(*args):
        self, data, raw = args
        if raw:
            print(json.dumps(data, indent=2))
        else:
            method(self, data)

    return print_raw


class BaseParser:
    asset = ''
    title_prop = 'name'
    key_prop = 'key'

    download_message = None
    has_description = True

    list_props = ()
    asset_props = ()

    @staticmethod
    def _print_markdown(text, indent):
        paragraphs = text.splitlines()
        # first paragraph
        wrapper = textwrap.TextWrapper(subsequent_indent=' ' * indent, width=70 + indent)
        lines = wrapper.wrap(paragraphs[0])
        for line in lines:
            print(line)

        # other paragraphs
        wrapper.initial_indent = ' ' * indent
        for paragraph in paragraphs[1:]:
            if paragraph:
                lines = wrapper.wrap(paragraph)
                for line in lines:
                    print(line)
            else:
                print()

    @handle_raw_option
    def print_list(self, items):
        columns = []
        props = (('Key', self.key_prop), ('Name', self.title_prop)) + self.list_props
        for prop in props:
            column = []
            prop_name, prop_key = prop
            column.append(prop_name.upper())
            for item in items:
                column.append(str(get_prop_value(item, prop_key)))
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

    def _get_asset_prop_length(self):
        props = ['key'] + [prop for prop, _ in self.asset_props]
        max_prop_length = max([len(x) for x in props])
        prop_length = (math.ceil(max_prop_length / 4) + 1) * 4
        return prop_length

    def _print_single_props(self, item, prop_length):
        props = (('key', self.key_prop), ('name', self.title_prop)) + self.asset_props
        for prop in props:
            prop_name, prop_key = prop
            name = prop_name.upper().ljust(prop_length)
            value = get_prop_value(item, prop_key)
            if isinstance(value, list):
                if value:
                    print(name, end='')
                    padding = ' ' * prop_length
                    for i, v in enumerate(value):
                        if i == 0:
                            print(f'- {v}')
                        else:
                            print(f'{padding}- {v}')
                else:
                    print(f'{name} None')
            else:
                print(f'{name}{value}')

    @handle_raw_option
    def print_single(self, item):
        prop_length = self._get_asset_prop_length()
        self._print_single_props(item, prop_length)

        key = get_prop_value(item, self.key_prop)

        if self.download_message:
            print()
            print(self.download_message)
            print(f'    substra download {self.asset} {key}')

        if self.has_description:
            print()
            print('Display this asset description:')
            print(f'    substra describe {self.asset} {key}')


class JsonOnlyParser:
    @staticmethod
    def _print(data):
        print(json.dumps(data, indent=2))

    def print_list(self, items, raw):
        self._print(items)

    def print_single(self, item, raw):
        self._print(item)


class AlgoParser(BaseParser):
    asset = 'algo'

    download_message = 'Download this algorithm\'s code:'


class ObjectiveParser(BaseParser):
    asset = 'objective'
    list_props = (
        ('Metrics', 'metrics.name'),
    )
    asset_props = (
        ('Metrics', 'metrics.name'),
        ('Test dataset', 'testDataset.dataManagerKey'),
        ('Test data samples', 'testDataset.dataSampleKeys'),
    )
    download_message = 'Download this objective\'s metric:'


class DatasetParser(BaseParser):
    asset = 'dataset'
    list_props = (
        ('Type', 'type'),
    )
    asset_props = (
        ('Objective key', 'objectiveKey'),
        ('Type', 'type'),
        ('Train data sample keys', 'trainDataSampleKeys'),
        ('Test data sample keys', 'testDataSampleKeys'),
    )
    download_message = 'Download this data manager\'s opener:'


class TraintupleParser(BaseParser):
    asset = 'traintuple'
    title_prop = lambda _, item: f'{get_recursive(item, "algo.name")}-{get_recursive(item, "key")[:4]}'  # noqa: E731, E501

    list_props = (
        ('Status', 'status'),
        ('Score', 'dataset.perf')
    )
    asset_props = (
        ('Model key', 'outModel.hash'),
        ('Algo key', 'algo.hash'),
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
    asset = 'testtuple'
    title_prop = lambda _, item: f'{get_recursive(item, "algo.name")}-{get_recursive(item, "model.traintupleKey")[:4]}'  # noqa: E731, E501
    list_props = (
        ('Certified', 'certified'),
        ('Status', 'status'),
        ('Score', 'dataset.perf')
    )
    asset_props = (
        ('Traintuple key', 'model.traintupleKey'),
        ('Algo key', 'algo.hash'),
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
