import logging

logger = logging.getLogger(__name__)


class SDKException(Exception):
    pass


class LoadDataException(SDKException):
    pass


class RequestException(SDKException):
    # TODO add factory method to create exception from request exception to have
    #      a simpler constructor
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
    def __init__(self, request_exception, msg=None):
        super(InternalServerError, self).__init__(request_exception, msg=msg)
        logger.debug(request_exception.response.text)


class InvalidRequest(HTTPError):
    def __init__(self, request_exception, msg=None):
        error = request_exception.response.json()
        message = error.get('message', None)
        logger.debug(f"Invalid request: error='{error}'")
        super(InvalidRequest, self).__init__(request_exception, message)


class NotFound(HTTPError):
    pass


class RequestTimeout(HTTPError):
    def __init__(self, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()

        try:
            pkhash = r['pkhash'] if 'pkhash' in r else r['message'].get('pkhash')
        except (AttributeError, KeyError):
            # XXX this is the case when doing a POST query to update the
            #     data manager for instance
            pkhash = None

        self.pkhash = pkhash

        msg = f"Operation on object with key(s) '{pkhash}' timed out."

        super(RequestTimeout, self).__init__(request_exception, msg=msg)


class AlreadyExists(HTTPError):
    def __init__(self, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()
        # XXX support list of pkhashes; this could be the case when adding
        #     a list of data samples through a single POST request
        if isinstance(r, list):
            pkhash = [x['pkhash'] for x in r]
        else:
            pkhash = r['pkhash']

        self.pkhash = pkhash

        msg = f"Object with key(s) '{pkhash}' already exists."

        super(AlreadyExists, self).__init__(request_exception, msg=msg)


class InvalidResponse(SDKException):
    def __init__(self, response, msg):
        self.response = response
        super(InvalidResponse, self).__init__(msg)
