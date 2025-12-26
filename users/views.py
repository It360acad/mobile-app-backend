from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from users.models import User
from users.serializer import UserDetailSerializer, UserUpdateSerializer


# User List View
@extend_schema(
  tags=['Users'],
  summary="List Users",
  description="Get a list of all users in the database.",
)
class UserListView(ListAPIView):
  queryset = User.objects.all()
  serializer_class = UserDetailSerializer
  permission_classes = [IsAuthenticated]


# User Retrieve View
@extend_schema(
  tags=['Users'],
  summary="Retrieve User",
  description="Get a specific user by their primary key (pk).",
)
class UserRetrieveView(RetrieveAPIView):
  queryset = User.objects.all()
  serializer_class = UserDetailSerializer
  permission_classes = [IsAuthenticated]


# User Update View
@extend_schema(
  tags=['Users'],
  summary="Update User",
  description="Update a specific user by their primary key (pk).",
)
class UserUpdateView(UpdateAPIView):
  queryset = User.objects.all()
  serializer_class = UserUpdateSerializer
  permission_classes = [IsAuthenticated]