import json

import requests
from substra_sdk_py.config import requests_get_params

from substra.commands.api import ALGO_ASSET, OBJECTIVE_ASSET, DATASET_ASSET, DATA_MANAGER_ASSET, TRAINTUPLE_ASSET, \
    TESTTUPLE_ASSET


def get_recursive(obj, key):
    def _inner(o, keys):
        k, *keys = keys
        if keys:
            return _inner(o.get(k, {}), keys)
        return o.get(k, None)
    return _inner(obj, key.split('.'))


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
    asset_props = (

    )

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

    @handle_raw_option
    def print_list(self, items):
        self._print_hr_count(items)
        for item in items:
            print(f'* {get_recursive(item, self.title_prop)}')
            print(f'  Key: {get_recursive(item, self.key_prop)}')
            for prop in self.list_props:
                prop_name, prop_key = prop
                print(f'  {prop_name}: {get_recursive(item, prop_key)}')

    @handle_raw_option
    def print_asset(self, item):
        print(f'KEY: {get_recursive(item, self.key_prop)}')
        for prop in self.asset_props:
            name, key = prop
            value = get_recursive(item, key)
            if isinstance(value, list):
                if value:
                    print(f'{name.upper()}:')
                    for v in value:
                        print(f'  * {v}')
                else:
                    print(f'{name.upper()}: None')
            else:
                print(f'{name.upper()}: {value}')
        if self.description_prop:
            desc = get_recursive(item, self.description_prop)
            url = desc.get('storageAddress')
            kwargs, headers = requests_get_params(self.client.config)
            r = requests.get(url, headers=headers, **kwargs)
            print('DESCRIPTION:')
            print(r.text)


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


class TesttupleParser(BaseParser):
    asset = 'Testtuple'


PARSERS = {
    ALGO_ASSET: AlgoParser,
    OBJECTIVE_ASSET: ObjectiveParser,
    DATA_MANAGER_ASSET: DatasetParser,
    TRAINTUPLE_ASSET: TraintupleParser,
    TESTTUPLE_ASSET: TesttupleParser,
}


def get_parser(asset, client):
    return PARSERS[asset](client) if asset in PARSERS else JsonOnlyParser()


