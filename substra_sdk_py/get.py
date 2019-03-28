import requests

from .config import requests_get_params


def get(asset, pkhash, config):

    kwargs, headers = requests_get_params(config)
    url = '%s/%s/%s' % (config['url'], asset, pkhash)

    try:
        r = requests.get(url, headers=headers, **kwargs)
    except:
        raise Exception('Failed to get %s' % asset)
    else:
        res = ''
        try:
            result = r.json()
            res = {'result': result, 'status_code': r.status_code}
        except:
            res = r.content
        finally:
            return res
