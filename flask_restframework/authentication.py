import base64
import binascii
import jwt

from flask import request, current_app, g
from . import exceptions

def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.headers.get("Authorization", b"")
    if isinstance(auth, str):
        return auth.encode("utf-8")
    return auth

class BaseAuthentication:
    """
    All authentication classes should extend BaseAuthentication.
    """
    def check_auth_inf(self, *args, **kwargs):
        """
        in authenticate() method we should call this method to check authorization information
        if check error, return False and error message
        """
        return True, ""

    def authenticate(self):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        raise NotImplementedError(".authenticate() must be overridden.")

    def authenticate_header(self):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        pass

class BasicAuthentication(BaseAuthentication):
    """
    HTTP Basic authentication against username/password.
    """

    www_authenticate_realm = 'api'

    def authenticate(self):
        """
        Returns User and {username, password} if correct
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'basic':
            return None

        if len(auth) == 1:
            msg = 'Invalid basic header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid basic header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            try:
                auth_decoded = base64.b64decode(auth[1]).decode('utf-8')
            except UnicodeDecodeError:
                auth_decoded = base64.b64decode(auth[1]).decode('latin-1')
            auth_parts = auth_decoded.partition(':')
        except (TypeError, UnicodeDecodeError, binascii.Error):
            msg = 'Invalid basic header. Credentials not correctly base64 encoded.'
            raise exceptions.AuthenticationFailed(msg)

        userid, password = auth_parts[0], auth_parts[2]
        auth_inf = {"id":userid,"password":password}

        passed, msg = self.check_auth_inf(**auth_inf)
        if not passed:
            raise exceptions.AuthenticationFailed(msg)

        g.current_user = current_app.USER_CLASS(**auth_inf)
        g.auth_inf = auth_inf
        return g.current_user, auth_inf

    def authenticate_header(self):
        return 'Basic realm="%s"' % self.www_authenticate_realm

class JWTAuthentication(BaseAuthentication):
    """
    HTTP Bearer authentication .
    """
    def check_auth_inf(self, *args, **kwargs):
        if "id" not in kwargs:
            return False, "'id' field not found in jwt payload"
        return True, ""

    def authenticate(self):
        """
        Returns User and payload of jwt if correct
        using HTTP Bearer authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = 'Invalid bearer header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid bearer header. Credentials string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        secret = current_app.config.get("JWT_SECRET")
        if not secret:
            msg = 'lost JWT_SECRET configuration'
            raise exceptions.ConfigureError(msg)
        try:
            payload = jwt.decode(auth[1].decode("utf8"), secret, algorithms=["HS256", "RS256"])
        except Exception as e:
            raise exceptions.AuthenticationFailed(e.__str__())

        passed, msg = self.check_auth_inf(**auth_inf)
        if not passed:
            raise exceptions.AuthenticationFailed(msg)

        g.current_user = current_app.USER_CLASS(**payload)
        g.auth_inf = payload
        return g.current_user, payload

    def authenticate_header(self):
        return "Bearer"