import requests


def path(asset, pkhash, path, config):

    kwargs = {}
    if config['auth']:
        kwargs.update({'auth': (config['auth']['user'], config['auth']['password'])})
    if config['insecure']:
        kwargs.update({'verify': False})

    url = '%s/%s/%s/%s' % (config['url'], asset, pkhash, path)
    headers = {'Accept': 'application/json;version=%s' % config['version']}
    try:
        r = requests.get(url, headers=headers, **kwargs)
    except:
        raise Exception('Failed to get path %s on %s' % (path, asset))
    else:
        res = ''
        try:
            result = r.json()
            res = {'result': result, 'status_code': r.status_code}
        except:
            res = r.content
        finally:
            return res
