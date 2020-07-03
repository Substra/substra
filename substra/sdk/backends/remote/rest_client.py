# Copyright 2018 Owkin, inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging
import time

import requests

from substra.sdk import exceptions, utils

logger = logging.getLogger(__name__)


class Client():
    """REST Client to communicate with Substra server."""

    def __init__(self, url, version, insecure, token):
        self._default_kwargs = {
            'verify': not insecure,
        }
        self._headers = {
            'Authorization': f"Token {token}",
            'Accept': f'application/json;version={version}',
        }
        if not url:
            raise exceptions.SDKException("url required to connect to the Substra server")
        self._base_url = url[:-1] if url.endswith('/') else url

    def login(self, username, password):
        # we do not use self._headers in order to avoid existing tokens to be sent alongside the
        # required Accept header
        if 'Accept' not in self._headers:
            raise exceptions.SDKException("Cannot login: missing headers")

        headers = {
            'Accept': self._headers['Accept'],
        }
        data = {
            'username': username,
            'password': password,
        }

        try:
            r = requests.post(f'{self._base_url}/api-token-auth/',
                              data=data,
                              headers=headers)
            r.raise_for_status()
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectionError.from_request_exception(e)
        except requests.exceptions.Timeout as e:
            raise exceptions.Timeout.from_request_exception(e)
        except requests.exceptions.HTTPError as e:
            logger.error(f"Requests error status {e.response.status_code}: {e.response.text}")

            if e.response.status_code in (400, 401):
                raise exceptions.BadLoginException.from_request_exception(e)

            raise exceptions.HTTPError.from_request_exception(e)

        token = r.json()['token']

        self._headers['Authorization'] = f"Token {token}"

        return token

    def __request(self, request_name, url, **request_kwargs):
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

        # rewind files so that they are properly sent in retries as well
        if 'files' in kwargs:
            for file in kwargs['files'].values():
                file.seek(0)

        # do HTTP request and catch generic exceptions
        try:
            r = fn(url, headers=self._headers, **kwargs)
            r.raise_for_status()

        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectionError.from_request_exception(e)

        except requests.exceptions.Timeout as e:
            raise exceptions.Timeout.from_request_exception(e)

        except requests.exceptions.HTTPError as e:
            logger.error(f"Requests error status {e.response.status_code}: {e.response.text}")

            if e.response.status_code == 400:
                raise exceptions.InvalidRequest.from_request_exception(e)

            if e.response.status_code == 401:
                raise exceptions.AuthenticationError.from_request_exception(e)

            if e.response.status_code == 403:
                raise exceptions.AuthorizationError.from_request_exception(e)

            if e.response.status_code == 404:
                raise exceptions.NotFound.from_request_exception(e)

            if e.response.status_code == 408:
                raise exceptions.RequestTimeout.from_request_exception(e)

            if e.response.status_code == 409:
                raise exceptions.AlreadyExists.from_request_exception(e)

            if e.response.status_code == 500:
                raise exceptions.InternalServerError.from_request_exception(e)

            if e.response.status_code in [502, 503, 504]:
                raise exceptions.GatewayUnavailable.from_request_exception(e)

            raise exceptions.HTTPError.from_request_exception(e)

        return r

    def _request(self, request_name, url, **request_kwargs):
        """Wrapper to __request to emit a log for each HTTP request."""
        ts = time.time()
        error = None
        try:
            return self.__request(request_name, url, **request_kwargs)
        except Exception as e:
            error = e.__class__.__name__
            raise
        finally:
            te = time.time()
            elaps = (te - ts) * 1000
            logger.debug(f'{request_name} {url}: done in {elaps:.2f}ms error={error}')

    @utils.retry_on_exception(exceptions=(exceptions.GatewayUnavailable))
    def request(self, request_name, asset_name, path=None, json_response=True,
                **request_kwargs):
        """Base request."""

        path = path or ''
        url = f"{self._base_url}/{asset_name}/{path}"
        if not url.endswith("/"):
            url = url + "/"  # server requires a suffix /

        response = self._request(
            request_name,
            url,
            **request_kwargs,
        )

        if not json_response:
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

        # the server always responds with a list of lists (linked to the debug option "is_complex")
        # which must then be flatten
        if isinstance(items, list) and all([isinstance(i, list) for i in items]):
            items = utils.flatten(items)

        return items

    def _add(self, name, exist_ok=False, **request_kwargs):
        """ Add asset wrapper.

        Handles conflict error when created asset already exists.
        """
        try:
            return self.request('post', name, **request_kwargs)

        except exceptions.AlreadyExists as e:
            if not exist_ok:
                raise

            key = e.pkhash or e.computePlanID
            is_many = isinstance(key, list)
            if is_many:
                logger.warning("Many assets not compatible with 'exist_ok' option")
                raise

            logger.warning(f"{name} already exists: key='{key}'")
            return self.get(name, key)

    def add(self, name, retry_timeout=False, exist_ok=False, **request_kwargs):
        """Add asset.

        In case of timeout, block till resource is created.

        If `exist_ok` is true, `AlreadyExists` exceptions will be ignored and the
        existing asset will be returned.
        """
        try:
            return self._add(name, exist_ok=exist_ok, **request_kwargs)

        except exceptions.RequestTimeout as e:
            key = e.pkhash
            is_many = isinstance(key, list)  # timeout on many objects is not handled
            if not retry_timeout or is_many:
                raise e

            logger.warning(
                f'Request timeout, blocking till {name} is created: key={key}')
            retry = utils.retry_on_exception(
                exceptions=(exceptions.RequestTimeout),
                timeout=float(retry_timeout),
            )
            # XXX as there is no guarantee that the request has been sent to the ledger
            #     (and will be processed), retry on on the add request and ignore
            #     potential conflicts
            return retry(self._add)(name, exist_ok=True, **request_kwargs)

    def get_data(self, address, **request_kwargs):
        """Get asset data."""
        return self._request(
            'get',
            address,
            **request_kwargs,
        )
