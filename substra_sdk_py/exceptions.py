class SDKException(Exception):
    pass


class RequestException(SDKException):
    def __init__(self, request_exn, msg=None):
        self.exn = request_exn
        if msg is None:
            msg = str(request_exn)
        else:
            msg = msg + ": {}".format(str(request_exn))
        super(RequestException, self).__init__(msg)

    @property
    def response(self):
        return self.exn.response

    @property
    def status_code(self):
        return self.response.status_code


class ConnectionError(RequestException):
    pass


class Timeout(RequestException):
    pass


class HTTPError(RequestException):
    pass


class AssetNotFound(HTTPError):
    pass


class AssetAlreadyExist(HTTPError):
    pass


class InvalidResponse(SDKException):
    def __init__(self, exn, response, msg=None):
        self.response = response
