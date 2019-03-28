import requests

from . import http_cli



def bulkUpdate(asset, data, config):
    url = '%s/%s/bulk_update/' % (config['url'], asset)
    return http_cli.post(config, url, data)
