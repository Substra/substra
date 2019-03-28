import requests

from .config import requests_get_params


def path(asset, pkhash, path, config):

    kwargs, headers = requests_get_params(config)
    url = '%s/%s/%s/%s' % (config['url'], asset, pkhash, path)

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
