import logging
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from users.models import User
from users.serializers import UserDetailSerializer, UserUpdateSerializer

# Get the logger named 'users'
logger = logging.getLogger('users')


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

  def get(self, request, *args, **kwargs):
    logger.info(
      f"User {request.user.email} is retrieving the list of all users.",
      extra={
        'tenant_id': 'N/A',
        'user_id': request.user.id
      }
    )
    return super().get(request, *args, **kwargs)


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

