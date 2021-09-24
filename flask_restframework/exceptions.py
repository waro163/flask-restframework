
from flask import jsonify
from . import status


class APIException(Exception):
    """
    Base class for REST framework exceptions.
    Subclasses should provide `.status_code` and `.default_detail` properties.
    """
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = detail
        self.code = code


    def __str__(self):
        return str(self.detail)

class ConfigureError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'server configuration error.'
    default_code = 'internal configure error'

class ValidationError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid input.'
    default_code = 'invalid'

class ParseError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Malformed request.'
    default_code = 'parse_error'


class AuthenticationFailed(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Incorrect authentication credentials.'
    default_code = 'authentication_failed'


class NotAuthenticated(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication credentials were not provided.'
    default_code = 'not_authenticated'


class PermissionDenied(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'


class NotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not found.'
    default_code = 'not_found'

def exception_handler(exc:Exception):
    '''
    Returns the response that should be used for any given exception.
    '''
    if not isinstance(exc, APIException):
        return jsonify({
            "message":exc.__str__(),
            "code":'A server error occurred.'
        }),status.HTTP_500_INTERNAL_SERVER_ERROR

    response = jsonify({"message":exc.detail,
                        "code":exc.code,
                    })
    response.status_code = exc.status_code
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        # WWW-Authenticate header for 401 responses, else coerce to 403
        if getattr(exc, 'auth_header', None):
            response.headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, 'wait', None):
            response.headers['Retry-After'] = '%d' % exc.wait
    return response