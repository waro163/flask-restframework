from flask import g, request

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

class BasePermission(object):

    def has_permission(self):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        raise NotImplementedError(".has_permission() must be overridden.")

class AllowAny(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self):
        return True

class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self):
        return bool(g.current_user and g.current_user.is_authenticated)

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    The request is authenticated as a user, or is a read-only request.
    """

    def has_permission(self):
        return bool(
            request.method in SAFE_METHODS or
            g.current_user and 
            g.current_user.is_authenticated
        )