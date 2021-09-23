from flask import current_app, g
from flask import views, jsonify, make_response
from . import exceptions

class APIView(views.MethodView):

    authentication_classes = current_app.AUTHENTICATION_CLASSES
    # throttle_classes = current_app.THROTTLE_CLASSES
    permission_classes = current_app.PERMISSION_CLASSES
    exception_handler = current_app.EXCEPTION_HANDLER

    def dispatch_request(self, *args, **kwargs):
        try:
            self.initial()
        except Exception as exc:
            return self.handle_exception(exc)
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
            try:
                user_auth_tuple = authenticator.authenticate()
            except exceptions.APIException as exc:
                exc.auth_header = authenticator.authenticate_header()
                raise exc
        
            if user_auth_tuple is not None:
                self.successful_authenticated = True
                self.authenticator = authenticator
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
            exc = exceptions.NotAuthenticated()
            exc.auth_header = self.get_authenticate_header()
            raise exc
        raise exceptions.PermissionDenied(detail=message, code=code)

    def get_authenticate_header(self):
        """
        If a request is unauthenticated, determine the WWW-Authenticate
        header to use for 401 responses, if any.
        """
        if self.authenticators:
            return self.authenticators[0].authenticate_header()

    def handle_exception(self, exc):
        """
        Handle any exception that occurs, by returning an appropriate response,
        or re-raising the error.
        """
        exception_handler = self.exception_handler
        return exception_handler(exc)