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
            msg = request_exception.response.json()["message"]
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
            msg = get_method("message", str(error))
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
            key = r["key"] if "key" in r else r["message"].get("key")
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
