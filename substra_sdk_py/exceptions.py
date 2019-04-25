class SDKException(Exception):
    pass


class RequestException(SDKException):
    def __init__(self, request_exception, msg=None):
        self.exception = request_exception
        if msg is None:
            msg = str(request_exception)
        else:
            msg = f"{request_exception}: {msg}"
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


class InternalServerError(HTTPError):
    pass


class InvalidRequest(HTTPError):
    pass


class NotFound(HTTPError):
    pass


class RequestTimeout(HTTPError):
    def __init__(self, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()
        pkhash = r['pkhash'] if 'pkhash' in r else r['message'].get('pkhash')

        self.pkhash = pkhash

        msg = f"Operation on object with key '{pkhash}' timed out."

        super(RequestTimeout, self).__init__(request_exception, msg=msg)


class AlreadyExists(HTTPError):
    def __init__(self, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()
        # XXX support list of pkhashes; this could be the case when adding
        #     a list of data samples through a single POST request
        pkhash = [x['pkhash'] for x in r] if isinstance(r, list) else \
            r['pkhash']

        self.pkhash = pkhash

        msg = f"Object with key '{pkhash}' already exists."

        super(AlreadyExists, self).__init__(request_exception, msg=msg)


class InvalidResponse(SDKException):
    def __init__(self, response, msg):
        self.response = response
        super(InvalidResponse, self).__init__(msg)
