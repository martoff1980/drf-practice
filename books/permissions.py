from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Allows all users to read,
    but only administrators to modify, create, or delete
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or (
                request.user and request.user.is_staff
            )
        )
