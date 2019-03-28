import requests

from . import http_cli


def update(asset, pkhash, data, config):
    url = '%s/%s/%s/update_ledger/' % (config['url'], asset, pkhash)
    return http_cli.post(config, url, data)
