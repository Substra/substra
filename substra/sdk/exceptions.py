import logging
from typing import Union

import requests

logger = logging.getLogger(__name__)


class SDKException(Exception):
    pass


class LoadDataException(SDKException):
    pass


class RequestException(SDKException):
    def __init__(self, msg, status_code):
        self.msg = msg
        self.status_code = status_code
        super().__init__(msg)

    @classmethod
    def from_request_exception(cls, request_exception):
        msg = None
        try:
            msg = request_exception.response.json()["detail"]
            msg = f"{request_exception}: {msg}"
        except Exception:
            msg = str(request_exception)

        try:
            status_code = request_exception.response.status_code
        except AttributeError:
            status_code = None

        return cls(msg, status_code)


class ConnectionError(RequestException):
    pass


class Timeout(RequestException):
    pass


class HTTPError(RequestException):
    pass


class InternalServerError(HTTPError):
    pass


class GatewayUnavailable(HTTPError):
    pass


class InvalidRequest(HTTPError):
    def __init__(self, msg, status_code, errors=None):
        super().__init__(msg, status_code)
        self.errors = errors

    @classmethod
    def from_request_exception(cls, request_exception):
        try:
            error = request_exception.response.json()
        except ValueError:
            error = request_exception.response

        get_method = getattr(error, "get", None)
        if callable(get_method):
            msg = get_method("detail", str(error))
        else:
            msg = str(error)

        try:
            status_code = request_exception.response.status_code
        except AttributeError:
            status_code = None

        return cls(msg, status_code, error)


class NotFound(HTTPError):
    pass


class RequestTimeout(HTTPError):
    def __init__(self, key, status_code):
        self.key = key
        msg = f"Operation on object with key(s) '{key}' timed out."
        super().__init__(msg, status_code)

    @classmethod
    def from_request_exception(cls, request_exception):
        # parse response and fetch key
        r = request_exception.response.json()

        try:
            key = r["key"] if "key" in r else r["detail"].get("key")
        except (AttributeError, KeyError):
            # XXX this is the case when doing a POST query to update the
            #     data manager for instance
            key = None

        return cls(key, request_exception.response.status_code)


class AlreadyExists(HTTPError):
    def __init__(self, key, status_code):
        self.key = key
        msg = f"Object with key(s) '{key}' already exists."
        super().__init__(msg, status_code)

    @classmethod
    def from_request_exception(cls, request_exception):
        # parse response and fetch key
        r = request_exception.response.json()
        # XXX support list of keys; this could be the case when adding
        #     a list of data samples through a single POST request
        if isinstance(r, list):
            key = [x["key"] for x in r]
        elif isinstance(r, dict):
            key = r.get("key", None)
        else:
            key = r

        return cls(key, request_exception.response.status_code)


class InvalidResponse(SDKException):
    def __init__(self, response, msg):
        self.response = response
        super(InvalidResponse, self).__init__(msg)


class AuthenticationError(HTTPError):
    pass


class AuthorizationError(HTTPError):
    pass


class BadLoginException(RequestException):
    """The server refused to log-in with these credentials"""

    pass


class UsernamePasswordLoginDisabledException(RequestException):
    """The server disabled the endpoint, preventing the use of Client.login"""

    @classmethod
    def from_request_exception(cls, request_exception):
        base = super().from_request_exception(request_exception)
        return cls(
            base.msg
            + (
                "\n\nAuthenticating with username/password is disabled.\n"
                "Log onto the frontend for your instance and generate a token there, "
                'then use it in the Client(token="...") constructor: '
                "https://docs.substra.org/en/stable/documentation/api_tokens_generation.html"
            ),
            base.status_code,
        )


def from_request_exception(
    e: requests.exceptions.RequestException,
) -> Union[RequestException, requests.exceptions.RequestException]:
    """
    try turning an exception from the `requests` library into a Substra exception
    """
    connection_error_mapping: dict[requests.exceptions.RequestException, RequestException] = {
        requests.exceptions.ConnectionError: ConnectionError,
        requests.exceptions.Timeout: Timeout,
    }
    for k, v in connection_error_mapping.items():
        if isinstance(e, k):
            return v.from_request_exception(e)

    http_status_mapping: dict[int, RequestException] = {
        400: InvalidRequest,
        401: AuthenticationError,
        403: AuthorizationError,
        404: NotFound,
        408: RequestTimeout,
        409: AlreadyExists,
        500: InternalServerError,
        502: GatewayUnavailable,
        503: GatewayUnavailable,
        504: GatewayUnavailable,
    }
    if isinstance(e, requests.exceptions.HTTPError):
        logger.error(f"Requests error status {e.response.status_code}: {e.response.text}")
        return http_status_mapping.get(e.response.status_code, HTTPError).from_request_exception(e)

    return e


class ConfigurationInfoError(SDKException):
    """ConfigurationInfoError"""

    pass


class BadConfiguration(SDKException):
    """Bad configuration"""

    pass


class UserException(SDKException):
    """User Exception"""

    pass


class EmptyInModelException(SDKException):
    """No in_models when needed"""

    pass


class ComputePlanKeyFormatError(Exception):
    """The given compute plan key has to respect the UUID format."""

    pass


class OrderingFormatError(Exception):
    """The given ordering parameter has to respect expected format."""

    pass


class FilterFormatError(Exception):
    """The given filters has to respect expected format."""

    pass


class NotAllowedFilterError(Exception):
    """The given filter is not available on asset."""

    pass


class KeyAlreadyExistsError(Exception):
    """The asset key has already been used."""

    pass


class _TaskAssetError(Exception):
    """Base exception class for task asset error"""

    def __init__(self, *, compute_task_key: str, identifier: str, message: str):
        self.compute_task_key = compute_task_key
        self.identifier = identifier
        self.message = message
        super().__init__(self.message)

    pass


class TaskAssetNotFoundError(_TaskAssetError):
    """Exception raised when no task input/output asset have not been found for specific task key and identifier"""

    def __init__(self, compute_task_key: str, identifier: str):
        message = f"No task asset found with {compute_task_key=} and {identifier=}"
        super().__init__(compute_task_key=compute_task_key, identifier=identifier, message=message)

    pass


class TaskAssetMultipleFoundError(_TaskAssetError):
    """Exception raised when more than one task input/output assets have been found for specific task key and
    identifier"""

    def __init__(self, compute_task_key: str, identifier: str):
        message = f"Multiple task assets found with {compute_task_key=} and {identifier=}"
        super().__init__(compute_task_key=compute_task_key, identifier=identifier, message=message)


class FutureError(Exception):
    """Error while waiting a blocking operation to complete"""


class FutureTimeoutError(FutureError):
    """Future execution timed out."""


class FutureFailureError(FutureError):
    """Future execution failed."""
