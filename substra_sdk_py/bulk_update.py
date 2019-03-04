import requests

from .config import ConfigManager


def bulkUpdate(asset, args, profile='default'):
    configManager = ConfigManager()
    config = configManager.get(profile)

    data = args

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['user'], config['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/bulk_update/' % (config['url'], asset)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.post(url, data=data, headers=headers, **kwargs)
    except:
        raise Exception('Failed to bulk update %s' % asset)
    else:
        try:
            res = r.json()
        except:
            res = r.content
        finally:
            return res
