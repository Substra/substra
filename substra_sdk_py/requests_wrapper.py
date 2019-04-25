import requests

from . import exceptions
from .config import requests_get_params


def _req(fn, config, url, **kwargs):

    default_kwargs, headers = requests_get_params(config)
    kwargs.update(default_kwargs)

    try:
        r = fn(url, headers=headers, **kwargs)
        r.raise_for_status()

    except requests.exceptions.ConnectionError as e:
        raise exceptions.ConnectionError(e)

    except requests.exceptions.Timeout as e:
        raise exceptions.Timeout(e)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise exceptions.InvalidRequest(e)

        if e.response.status_code == 404:
            raise exceptions.NotFound(e)

        if e.response.status_code == 408:
            raise exceptions.RequestTimeout(e)

        if e.response.status_code == 409:
            raise exceptions.AlreadyExists(e)

        raise exceptions.HTTPError(e)

    try:
        result = r.json()
    except ValueError as e:
        # we always expect JSON response from the server
        msg = "Cannot parse response to JSON: {}".format(str(e))
        raise exceptions.InvalidResponse(r, msg)

    return result


def post(config, url, data, **kwargs):
    return _req(requests.post, config, url, data=data, **kwargs)


def get(config, url, **kwargs):
    return _req(requests.get, config, url, **kwargs)


def options(config, url, **kwargs):
    return _req(requests.options, config, url, **kwargs)
