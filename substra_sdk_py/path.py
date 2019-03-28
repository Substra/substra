import requests

from . import http_cli


def path(asset, pkhash, path, config):
    url = '%s/%s/%s/%s' % (config['url'], asset, pkhash, path)
    return http_cli.get(config, url)
