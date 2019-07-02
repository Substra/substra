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

        if e.response.status_code == 500:
            raise exceptions.InternalServerError(e)

        raise exceptions.HTTPError(e)

    return r


def _jsonreq(fn, config, url, **kwargs):
    response = _req(fn, config, url, **kwargs)
    try:
        result = response.json()
    except ValueError as e:
        # we always expect JSON response from the server
        msg = f"Cannot parse response to JSON: {e}"
        raise exceptions.InvalidResponse(response, msg)

    return result


def post(config, url, data, **kwargs):
    return _jsonreq(requests.post, config, url, data=data, **kwargs)


def get(config, url, **kwargs):
    return _jsonreq(requests.get, config, url, **kwargs)


def options(config, url, **kwargs):
    return _jsonreq(requests.options, config, url, **kwargs)


def raw_get(config, url, **kwargs):
    return _req(requests.get, config, url, **kwargs)
