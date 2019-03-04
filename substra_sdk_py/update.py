import requests

from .config import ConfigManager


def update(asset, pkhash, data, profile='default'):
    configManager = ConfigManager()
    config = configManager.get(profile)

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['user'], config['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/%s/update_ledger/' % (config['url'], asset, pkhash)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.post(url, data=data, headers=headers, **kwargs)
    except:
        raise Exception('Failed to update %s' % asset)
    else:
        try:
            res = r.json()
        except:
            res = r.content
        finally:
            return res
