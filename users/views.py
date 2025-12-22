from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from users.serializer import UserSerializer


# User Profile View (Get and Update)
class UserProfileView(RetrieveUpdateAPIView):
  serializer_class = UserSerializer
  permission_classes = [IsAuthenticated]

  def get_object(self):
    return self.request.user

  # Password update is handled in the serializer