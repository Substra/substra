import json
import logging
import time
from typing import Dict
from typing import List
from typing import Union

import requests

from substra.sdk import exceptions
from substra.sdk import schemas
from substra.sdk import utils
from substra.sdk.backends.remote import request_formatter

logger = logging.getLogger(__name__)


class Client:
    """REST Client to communicate with Substra server."""

    @property
    def base_url(self) -> str:
        return self._base_url

    def __init__(self, url, insecure, token):
        self._default_kwargs = {
            "verify": not insecure,
        }
        self._headers = {
            "Authorization": f"Token {token}",
            "Accept": "application/json;version=0.0",
        }
        if not url:
            raise exceptions.SDKException("url required to connect to the Substra server")
        self._base_url = url[:-1] if url.endswith("/") else url

    def login(self, username, password):
        # we do not use self._headers in order to avoid existing tokens to be sent alongside the
        # required Accept header
        if "Accept" not in self._headers:
            raise exceptions.SDKException("Cannot login: missing headers")

        headers = {
            "Accept": self._headers["Accept"],
        }
        data = {
            "username": username,
            "password": password,
        }
        try:
            r = requests.post(f"{self._base_url}/api-token-auth/", data=data, headers=headers)
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

        try:
            token = r.json()["token"]
        except json.decoder.JSONDecodeError:
            # sometimes requests seem to be fine, but the json is not being found
            # this might be if the url seems to be correct (in the syntax)
            # but it's not the right one
            raise exceptions.BadConfiguration(
                "Unable to get token from json response. " f"Make sure that given url: {self._base_url} is correct"
            )
        self._headers["Authorization"] = f"Token {token}"

        return token

    # TODO: '__request' is too complex, consider refactoring
    def __request(self, request_name, url, **request_kwargs):  # noqa: C901
        """Base request helper."""

        if request_name == "get":
            fn = requests.get
        elif request_name == "post":
            fn = requests.post
        elif request_name == "put":
            fn = requests.put
        else:
            raise NotImplementedError

        # override default request arguments with input arguments
        kwargs = dict(self._default_kwargs)
        kwargs.update(request_kwargs)

        # rewind files so that they are properly sent in retries as well
        if "files" in kwargs:
            for file in kwargs["files"].values():
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

    @utils.retry_on_exception(exceptions=(exceptions.GatewayUnavailable))
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
            logger.debug(f"{request_name} {url}: done in {elaps:.2f}ms error={error}")

    def request(
        self,
        request_name: str,
        asset_type: str,
        path: str = None,
        json_response: bool = True,
        paginated: bool = False,
        **request_kwargs,
    ):
        """
        Base request

        Args:
            request_name (str): http rest method invoked. e.g. "get", "post" or "put"
            asset_type (str): asset type. e.g. "algo"
            path (str, optional): additional route e.g. "cp_key/perf" in /compute_plan/cp_key/perf. Defaults to None.
            json_response (bool, optional): whether the expected response is formatted in json. Defaults to True.
            paginated (bool, optional): whether the response would be paginated or not. Defaults to False.
            request_kwargs (dict): the args. The arg ["params"] is a dict with keys = attributes, values = list of
                values for this attribute. e.g. {name:[name1, name2]}

        Raises:
            exceptions.InvalidResponse:

        Returns:
            Union[requests.Response, dict, List] : the assets. Type: requests.Response if json_response is False, a dict
                if paginated is False, a List otherwise.
        """

        path = path or ""
        url = f"{self._base_url}/{asset_type}/{path}"
        if not url.endswith("/"):
            url = url + "/"  # server requires a suffix /

        # first request
        response = self._request(
            request_name,
            url,
            **request_kwargs,
        )

        if not json_response:
            return response

        try:
            json_resp = response.json()
            if not paginated:
                return json_resp
            # in case response is expected to be paginated, get all pages
            url_next = json_resp["next"]
            while url_next:
                resp = self._request(
                    request_name,
                    url_next,
                    **request_kwargs,
                )
                json_resp["results"].extend(resp.json()["results"])
                url_next = resp.json()["next"]
            # extract full asset list from returned structure
            return json_resp["results"]
        except ValueError as e:
            msg = f"Cannot parse response to JSON: {e}"
            raise exceptions.InvalidResponse(response, msg)

    def get(self, name, key):
        """Get asset by key."""
        return self.request(
            "get",
            name,
            path=f"{key}",
        )

    def list(
        self,
        asset_type: str,
        filters: Dict[str, Union[List[str], str, dict]] = None,
        order_by: str = None,
        ascending: bool = False,
        paginated: bool = True,
        path: str = None,
    ) -> List[Dict]:
        """List assets by filters.

        Args:
            asset_type (str): asset type. e.g. "algo"
            filters (dict, optional): keys = attributes, values = value(s) for this attribute
                (depends on the attribute, cf [sdk reference](references/sdk.md)).
                e.g. {"key": ["key1", "key2"]}. "," corresponds to an "OR". Defaults to None.
                                "," corresponds to an "OR".
            order_by (str, optional): attribute name to order the results on. Defaults to None.
                e.g. "name" for an ordering on name.
            ascending (bool, optional): to reverse ordering. Defaults to False (descending order).
            paginated (bool, optional): whether the response would be paginated or not. Defaults to True.
            path (str, optional): additional route e.g. "cp_key/perf" in /compute_plan/cp_key/perf. Defaults to None.

        Returns:
            List[Dict] : a List of assets (dicts)
        """

        request_kwargs = {"params": {}}
        if filters:
            request_kwargs["params"] = request_formatter.format_search_filters_for_remote(filters)
        if order_by:
            request_kwargs["params"]["ordering"] = request_formatter.format_search_ordering_for_remote(
                order_by, ascending
            )
        items = self.request("get", asset_type, path=path, paginated=paginated, **request_kwargs)

        return items

    def _add(self, name, **request_kwargs):
        """Add asset wrapper.

        Handles conflict error when created asset already exists.
        """
        try:
            return self.request("post", name, **request_kwargs)

        except exceptions.AlreadyExists as e:
            key = e.key
            is_many = isinstance(key, list)
            if is_many:
                logger.warning(
                    "AlreadyExists exception was received for a list of keys. "
                    "Unable to determine which key(s) already exist."
                )
                raise

            logger.warning(f"{name} already exists: key='{key}'")
            if name == schemas.Type.ComputePlan:
                # We only need to retrieve the full asset in the case of a Compute Plan.
                return self.get(name, key)
            else:
                return {"key": key}

    def add(self, name, retry_timeout=False, **request_kwargs):
        """Add asset.

        In case of timeout, block till resource is created.
        """
        try:
            return self._add(name, **request_kwargs)

        except exceptions.RequestTimeout as e:
            key = e.key
            is_many = isinstance(key, list)  # timeout on many objects is not handled
            if not retry_timeout or is_many:
                raise e

            logger.warning(f"Request timeout, blocking till {name} is created: key={key}")
            retry = utils.retry_on_exception(
                exceptions=(exceptions.RequestTimeout),
                timeout=float(retry_timeout),
            )
            # XXX as there is no guarantee that the request has been sent to the ledger
            #     (and will be processed), retry on on the add request and ignore
            #     potential conflicts
            return retry(self._add)(name, **request_kwargs)

    def _update(self, name, key, **request_kwargs):
        """Update asset wrapper."""
        return self.request("put", name, key, **request_kwargs)

    def update(self, name, key, retry_timeout=False, **request_kwargs):
        """Add asset.

        In case of timeout, block till resource is created.
        """
        try:
            return self._update(name, key, **request_kwargs)
        except exceptions.RequestTimeout as e:
            if not retry_timeout:
                raise e

            logger.warning(f"Request timeout, blocking till {name} is updated: key={key}")
            retry = utils.retry_on_exception(
                exceptions=(exceptions.RequestTimeout),
                timeout=float(retry_timeout),
            )
            # XXX as there is no guarantee that the request has been sent to the ledger
            #     (and will be processed), retry on the update request and ignore
            #     potential conflicts
            return retry(self._update)(name, key, **request_kwargs)

    def get_data(self, address, **request_kwargs):
        """Get asset data."""
        return self._request(
            "get",
            address,
            **request_kwargs,
        )
