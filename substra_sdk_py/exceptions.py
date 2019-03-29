class SDKException(Exception):
    pass


class RequestException(SDKException):
    def __init__(self, request_exception, msg=None):
        self.exception = request_exception
        if msg is None:
            msg = str(request_exception)
        else:
            msg = f"{msg}: {request_exception}"
        super(RequestException, self).__init__(msg)

    @property
    def response(self):
        return self.exception.response

    @property
    def status_code(self):
        return self.response.status_code


class ConnectionError(RequestException):
    pass


class Timeout(RequestException):
    pass


class HTTPError(RequestException):
    pass


class RequestTimeout(HTTPError):
    pass


class AssetNotFound(HTTPError):
    pass


class AssetAlreadyExist(HTTPError):
    pass


class InvalidResponse(SDKException):
    def __init__(self, response, msg):
        self.response = response
        super(InvalidResponse, self).__init__(msg)
