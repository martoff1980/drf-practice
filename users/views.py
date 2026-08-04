from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Эндпоинт для регистрации нового пользователя"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Эндпоинт /users/me/ для просмотра и редактирования своего профиля"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user