from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает чтение всем пользователям, 
    а изменение/создание/удаление — только администраторам.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )