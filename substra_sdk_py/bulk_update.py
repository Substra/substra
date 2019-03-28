import requests

from .config import requests_get_params


def bulkUpdate(asset, data, config):

    kwargs, headers = requests_get_params(config)
    url = '%s/%s/bulk_update/' % (config['url'], asset)

    try:
        r = requests.post(url, data=data, headers=headers, **kwargs)
    except:
        raise Exception('Failed to bulk update %s' % asset)
    else:
        res = ''
        try:
            result = r.json()
            res = {'result': result, 'status_code': r.status_code}
        except:
            res = r.content
        finally:
            return res
