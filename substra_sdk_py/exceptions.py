class _BaseException(Exception):
    pass


class RequestException(_BaseException):
    def __init__(self, request_exn):
        self.exn = request_exn

    @property
    def response(self):
        return self.exn.response

    @property
    def status_code(self):
        return self.response.status_code


class Timeout(RequestException):
    pass


class AssetNotFound(RequestException):
    pass


class AssetAlreadyExist(RequestException):
    pass


class InvalidResponse(_BaseException):
    def __init__(self, response):
        self.response = response
