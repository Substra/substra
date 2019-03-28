import functools

import requests

from .config import requests_get_params


def parse_response(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        r = f(*args, **kwargs)

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise

        try:
            result = r.json()
        except ValueError:
            # we always expect JSON response from the server
            raise ValueError("Cannot decode response: {}".format(r.content))

        return result
    return wrapper


@parse_response
def _req(fn, config, url, **kwargs):
    all_kwargs, headers = requests_get_params(config)
    all_kwargs.update(kwargs)

    try:
        r = fn(url, headers=headers, **all_kwargs)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        raise
    return r


def post(config, url, data, **kwargs):
    return _req(requests.post, config, url, data=data, **kwargs)


def get(config, url, **kwargs):
    return _req(requests.get, config, url, **kwargs)
