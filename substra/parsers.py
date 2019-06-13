import json

import requests
from substra_sdk_py.config import requests_get_params

from substra.commands.api import ALGO_ASSET


class JsonOnlyParser:
    @classmethod
    def print(cls, data, raw):
        print(json.dumps(data, indent=2))


class BaseListParser:
    def _print_hr_count(self, items):
        n = len(items)
        if n == 0:
            print(f'No {self.asset}s found.')
            return

        if n == 1:
            print(f'1 {self.asset} found.')
        else:
            print(f'{n} {self.asset}s found.')

    def _print_hr_item(self, item):
        print(f'* {item.get(self.item_title)}')
        for prop in self.item_props:
            prop_name, prop_key = prop
            print(f'  {prop_name}: {item.get(prop_key)}')

    def _print_hr(self, items):
        self._print_hr_count(items)
        for item in items:
            self._print_hr_item(item)

    def print(self, items, raw):
        if raw:
            print(json.dumps(items, indent=2))
        else:
            self._print_hr(items)


class AlgoListParser(BaseListParser):
    asset = 'Algo'
    item_title = 'name'
    item_props = (
        ('Key', 'key'),
    )


class BaseAssetParser:
    def __init__(self, client):
        self.client = client

    def _print_hr(self, item):
        for prop in self.item_props:
            name, key = prop
            print(f'{name.upper()}: {item.get(key)}')
        if self.description_key:
            desc = item.get(self.description_key)
            url = desc.get('storageAddress')
            kwargs, headers = requests_get_params(self.client.config)
            r = requests.get(url, headers=headers, **kwargs)
            print('DESCRIPTION')
            print(r.text)

    def print(self, item, raw):
        if raw:
            print(json.dumps(item, indent=2))
        else:
            self._print_hr(item)


class AlgoAssetParser(BaseAssetParser):
    asset = 'Algo'
    item_props = (
        ('Name', 'name'),
        ('Key', 'pkhash'),
    )
    description_key = 'description'


LIST_PARSERS = {
    ALGO_ASSET: AlgoListParser,
}

ASSET_PARSERS = {
    ALGO_ASSET: AlgoAssetParser,
}


class ParserNotFound(Exception):
    def __init__(self, asset, command):
        super().__init__(f'Could not find parser for asset "{asset}" and command "{command}"')


def get_list_parser(asset):
    return LIST_PARSERS[asset]() if asset in LIST_PARSERS else JsonOnlyParser()


def get_asset_parser(asset, client):
    return ASSET_PARSERS[asset](client) if asset in ASSET_PARSERS else JsonOnlyParser()
