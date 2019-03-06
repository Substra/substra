import requests


def path(asset, pkhash, path, config):

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['user'], config['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/%s/%s' % (config['url'], asset, pkhash, path)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.get(url, headers=headers, **kwargs)
    except:
        raise Exception('Failed to get path %s on %s' % (path, asset))
    else:
        try:
            res = r.json()
        except:
            res = r.content
        finally:
            return res
