import requests

from . import http_cli


def get(asset, pkhash, config):
    url = '%s/%s/%s' % (config['url'], asset, pkhash)
    return http_cli.get(config, url)
