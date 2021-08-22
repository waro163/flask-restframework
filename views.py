from flask import current_app, g
from flask import views, jsonify, make_response
from . import exceptions

class APIView(views.MethodView):

    authentication_classes = current_app.AUTHENTICATION_CLASSES
    # throttle_classes = current_app.THROTTLE_CLASSES
    permission_classes = current_app.PERMISSION_CLASSES

    def dispatch_request(self, *args, **kwargs):
        try:
            self.initial()
        except Exception as exc:
            response = jsonify({"message":exc.detail,
                                    "code":exc.code,
                                })
            response.status_code = exc.status_code
            if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
                # WWW-Authenticate header for 401 responses, else coerce to 403
                auth_header = self.authenticator.authenticate_header()
                response.headers["WWW-Authenticate"] = auth_header
                # response.headers['Retry-After'] = '%d' % exc.wait
            return response
        return super().dispatch_request(*args, **kwargs)

    def initial(self):
        self.perform_authentication()
        self.check_permissions()

    def get_authenticators(self):
        """
        Instantiates and returns the list of authenticators that this view can use.
        """
        self.authenticators = [auth() for auth in self.authentication_classes]
        return self.authenticators

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]

    def perform_authentication(self):
        self.successful_authenticated = False
        for authenticator in self.get_authenticators():
            self.authenticator = authenticator
            try:
                user_auth_tuple = authenticator.authenticate()
            except exceptions.APIException as e:
                raise e
        
            if user_auth_tuple is not None:
                self.successful_authenticated = True
                g.current_user, g.auth_inf = user_auth_tuple
                break

    def check_permissions(self):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission():
                self.permission_denied(
                    message=getattr(permission, 'message', None),
                    code=getattr(permission, 'code', None)
                )

    def permission_denied(self, message=None, code=None):
        """
        If request is not permitted, determine what kind of exception to raise.
        """
        if self.authenticators and not self.successful_authenticated:
            raise exceptions.NotAuthenticated()
        raise exceptions.PermissionDenied(detail=message, code=code)

