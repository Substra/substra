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
    def from_request_exception(cls, request_exception, msg=None):
        if msg is None:
            msg = str(request_exception)
        else:
            msg = f"{request_exception}: {msg}"

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
    @classmethod
    def from_request_exception(cls, request_exception):
        try:
            error = request_exception.response.json()
        except ValueError:
            error = request_exception.response
        msg = error.get('message', None)
        return super().from_request_exception(request_exception, msg)


class NotFound(HTTPError):
    pass


class RequestTimeout(HTTPError):
    def __init__(self, pkhash, status_code):
        self.pkhash = pkhash
        msg = f"Operation on object with key(s) '{pkhash}' timed out."
        super().__init__(msg, status_code)

    @classmethod
    def from_request_exception(cls, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()

        try:
            pkhash = r['pkhash'] if 'pkhash' in r else r['message'].get('pkhash')
        except (AttributeError, KeyError):
            # XXX this is the case when doing a POST query to update the
            #     data manager for instance
            pkhash = None

        return cls(pkhash, request_exception.response.status_code)


class AlreadyExists(HTTPError):
    def __init__(self, pkhash, status_code):
        self.pkhash = pkhash
        msg = f"Object with key(s) '{pkhash}' already exists."
        super().__init__(msg, status_code)

    @classmethod
    def from_request_exception(cls, request_exception):
        # parse response and fetch pkhash
        r = request_exception.response.json()
        # XXX support list of pkhashes; this could be the case when adding
        #     a list of data samples through a single POST request
        if isinstance(r, list):
            pkhash = [x['pkhash'] for x in r]
        else:
            pkhash = r['pkhash']

        return cls(pkhash, request_exception.response.status_code)


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


class KeyringException(SDKException):
    """Could not retrieve password from keyring"""
    pass
