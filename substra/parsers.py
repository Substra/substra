import json

import requests
import textwrap

from substra_sdk_py.config import requests_get_params

from substra.commands.api import ALGO_ASSET, OBJECTIVE_ASSET, DATA_MANAGER_ASSET, TRAINTUPLE_ASSET, \
    TESTTUPLE_ASSET


def get_recursive(obj, key):
    def _inner(o, keys):
        k, *keys = keys
        if keys:
            return _inner(o.get(k, {}), keys)
        return o.get(k, None)
    return _inner(obj, key.split('.'))


def get_prop_value(obj, key):
    if callable(key):
        return key(obj)
    return get_recursive(obj, key)


def handle_raw_option(method):
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
    description_prop = 'description'

    list_props = ()
    asset_props = ()

    def __init__(self, client):
        self.client = client

    def _print_hr_count(self, items):
        n = len(items)
        if n == 0:
            print(f'No {self.asset}s found.')
            return

        if n == 1:
            print(f'1 {self.asset} found.')
        else:
            print(f'{n} {self.asset}s found.')

    @staticmethod
    def _print_markdown(text, indent):
        paragraphs = text.splitlines()
        # first paragraph
        wrapper = textwrap.TextWrapper(subsequent_indent=' ' * indent, width=70+indent)
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
        prop_length = self._get_list_prop_length()
        self._print_hr_count(items)

        for item in items:
            title = get_prop_value(item, self.title_prop)
            print()
            print(title)
            print('='*len(title))
            print(f'{"KEY".ljust(prop_length)} {get_prop_value(item, self.key_prop)}')
            for prop in self.list_props:
                prop_name, prop_key = prop
                print(f'{prop_name.upper().ljust(prop_length)} {get_prop_value(item, prop_key)}')

    def _get_list_prop_length(self):
        props = ['key'] + [prop for prop, _ in self.list_props]
        max_prop_length = max(map(lambda x: len(x), props))
        return max_prop_length

    def _get_asset_prop_length(self):
        props = ['key'] + [prop for prop, _ in self.asset_props]
        if self.description_prop:
            props.append('description')
        max_prop_length = max(map(lambda x: len(x), props))
        return max_prop_length + 1

    def _print_asset_props(self, item, prop_length):
        print(f'{"KEY".ljust(prop_length)} {get_prop_value(item, self.key_prop)}')
        for prop in self.asset_props:
            name, key = prop
            value = get_prop_value(item, key)
            if isinstance(value, list):
                if value:
                    print(f'{name.upper().ljust(prop_length)}', end='')
                    padding = ' ' * prop_length
                    for i, v in enumerate(value):
                        if i == 0:
                            print(f'- {v}')
                        else:
                            print(f'{padding}- {v}')
                else:
                    print(f'{name.upper().ljust(prop_length)} None')
            else:
                print(f'{name.upper().ljust(prop_length)} {value}')

    def _print_description(self, item, prop_length):
        if self.description_prop:
            desc = get_prop_value(item, self.description_prop)
            url = desc.get('storageAddress')
            kwargs, headers = requests_get_params(self.client.config)
            r = requests.get(url, headers=headers, **kwargs)
            print('DESCRIPTION'.ljust(prop_length), end='')
            self._print_markdown(r.text, indent=prop_length)

    @handle_raw_option
    def print_asset(self, item):
        prop_length = self._get_asset_prop_length()
        self._print_asset_props(item, prop_length)
        self._print_description(item, prop_length)


class JsonOnlyParser:
    @staticmethod
    def _print(data):
        print(json.dumps(data, indent=2))

    def print_list(self, items, raw):
        self._print(items)

    def print_asset(self, item, raw):
        self._print(item)


class AlgoParser(BaseParser):
    asset = 'Algo'
    asset_props = (
        ('Name', 'name'),
    )


class ObjectiveParser(BaseParser):
    asset = 'Objective'
    list_props = (
        ('Metrics', 'metrics.name'),
    )
    asset_props = (
        ('Metrics', 'metrics.name'),
        ('Metrics script', 'metrics.storageAddress'),
    )


class DatasetParser(BaseParser):
    asset = 'Dataset'
    asset_props = (
        ('Opener', 'opener.storageAddress'),
        ('Train data sample keys', 'trainDataSampleKeys'),
        ('Test data sample keys', 'testDataSampleKeys'),
    )


class TraintupleParser(BaseParser):
    asset = 'Traintuple'
    title_prop = lambda _, item: f'{get_recursive(item, "algo.name")}-{get_recursive(item, "key")[:4]}'
    description_prop = None
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
    )


class TesttupleParser(BaseParser):
    asset = 'Testtuple'
    title_prop = lambda _, item: f'{get_recursive(item, "algo.name")}-{get_recursive(item, "model.traintupleKey")[:4]}'
    description_prop = None
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
    )


PARSERS = {
    ALGO_ASSET: AlgoParser,
    OBJECTIVE_ASSET: ObjectiveParser,
    DATA_MANAGER_ASSET: DatasetParser,
    TRAINTUPLE_ASSET: TraintupleParser,
    TESTTUPLE_ASSET: TesttupleParser,
}


def get_parser(asset, client):
    return PARSERS[asset](client) if asset in PARSERS else JsonOnlyParser()


