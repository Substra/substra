import requests


def get(asset, pkhash, config):

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['user'], config['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/%s' % (config['url'], asset, pkhash)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.get(url, headers=headers, **kwargs)
    except:
        raise Exception('Failed to get %s' % asset)
    else:
        try:
            res = r.json()
        except:
            res = r.content
        finally:
            return res
