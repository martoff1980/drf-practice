from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from users.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Endpoint for new user registration"""

    serializer_class = UserSerializer

    permission_classes = (AllowAny,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """The /users/me/ endpoint for viewing and editing one's profile"""

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
