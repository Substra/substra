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


class InvalidRequest(HTTPError):
    pass


class AssetNotFound(HTTPError):
    pass


class RequestTimeout(HTTPError):
    def __init__(self, request_exception, msg=None):
        super(RequestTimeout, self).__init__(request_exception, msg=msg)

        # parse response and fetch pkhash
        r = self.response.json()
        pkhash = r['pkhash'] if 'pkhash' in r else r['message'].get('pkhash')

        self.pkhash = pkhash


class AssetAlreadyExist(HTTPError):
    def __init__(self, request_exception, msg=None):
        super(AssetAlreadyExist, self).__init__(request_exception, msg=msg)

        # parse response and fetch pkhash
        r = self.response.json()
        # XXX support list of pkhashes; this could be the case when adding
        #     a list of data samples through a single POST request
        pkhash = [x['pkhash'] for x in r] if isinstance(r, list) else \
            r['pkhash']

        self.pkhash = pkhash


class InvalidResponse(SDKException):
    def __init__(self, response, msg):
        self.response = response
        super(InvalidResponse, self).__init__(msg)
