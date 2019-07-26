import logging
import requests

from substra.sdk import exceptions, assets, utils

logger = logging.getLogger(__name__)

DEFAULT_RETRY_TIMEOUT = 5 * 60


class Client():
    """REST Client to communicate with Substra server."""

    def __init__(self, config=None):
        self._headers = {}
        self._default_kwargs = {}
        self._base_url = None

        if config:
            self.set_config(config)

    def set_config(self, config):
        """Reset internal attributes from config."""
        # get default requests keyword arguments from config
        kwargs = {}
        if config['auth']:
            user, password = config['auth']['user'], config['auth']['password']
            kwargs['auth'] = (user, password)

        if config['insecure']:
            kwargs['verify'] = False

        # get default HTTP headers from config
        headers = {'Accept': 'application/json;version={}'.format(config['version'])}

        self._headers = headers
        self._default_kwargs = kwargs
        self._base_url = config['url']

    def _request(self, request_name, url, **request_kwargs):
        """Base request helper."""

        if request_name == 'get':
            fn = requests.get
        elif request_name == 'post':
            fn = requests.post
        else:
            raise NotImplementedError

        # override default request arguments with input arguments
        kwargs = dict(self._default_kwargs)
        kwargs.update(request_kwargs)

        # do HTTP request and catch generic exceptions
        try:
            r = fn(url, headers=self._headers, **kwargs)
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

    def request(self, request_name, asset_name, path=None, json=True,
                **request_kwargs):
        """Base request."""

        path = path or ''
        url = f"{self._base_url}/{assets.to_server_name(asset_name)}/{path}"
        if not url.endswith("/"):
            url = url + "/"  # server requires a suffix /

        response = self._request(
            request_name,
            url,
            **request_kwargs,
        )

        if not json:
            return response

        try:
            return response.json()
        except ValueError as e:
            msg = f"Cannot parse response to JSON: {e}"
            raise exceptions.InvalidResponse(response, msg)

    def get(self, name, key):
        """Get asset by key."""
        return self.request(
            'get',
            name,
            path=f"{key}",
        )

    def list(self, name, filters=None):
        """List assets by filters."""
        request_kwargs = {}
        if filters:
            request_kwargs['params'] = utils.parse_filters(filters)

        items = self.request(
            'get',
            name,
            **request_kwargs,
        )

        # when filtering 'complex' assets the server responds with a list per filter
        # item, these list of list must then be flatten
        if isinstance(items, list) and all([isinstance(i, list) for i in items]):
            items = utils.flatten(items)

        return items

    def add(self, name, retry_timeout=DEFAULT_RETRY_TIMEOUT, **request_kwargs):
        """Add asset.

        In case of timeout, block till resource is created.
        """
        try:
            return self.request(
                'post',
                name,
                **request_kwargs,
            )

        except exceptions.RequestTimeout as e:
            logger.warning(
                'Request timeout, blocking till asset is created')
            key = e.pkhash
            is_many = isinstance(key, list)  # timeout on many objects is not handled
            if not retry_timeout or is_many:
                raise e

            retry = utils.retry_on_exception(
                exceptions=(exceptions.NotFound),
                timeout=float(retry_timeout),
            )
            return retry(self.get)(name, key)

    def get_data(self, address, **request_kwargs):
        """Get asset data."""
        return self._request(
            'get',
            address,
            json=False,
            **request_kwargs,
        )
