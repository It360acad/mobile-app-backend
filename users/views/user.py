import logging
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from users.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserDetailSerializer, UserUpdateSerializer, LinkChildSerializer

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


class LinkChildView(APIView):
  permission_classes = [IsAuthenticated]

  @extend_schema(
    request=LinkChildSerializer,
    responses={200: UserDetailSerializer},
    tags=['Parents'],
    summary="Link Child to Parent",
    description="Link a student to a parent using the student's unique linking code.",
  )
  def post(self, request):
    # Ensure user is a parent
    if request.user.role != 'parent':
      return Response(
        {'error': 'Only parents can link children.'},
        status=status.HTTP_403_FORBIDDEN
      )
    
    serializer = LinkChildSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    student = serializer.link_child(request.user)
    
    return Response(
      {
        'message': f'Student {student.user.get_full_name()} linked successfully.',
        'student': UserDetailSerializer(student.user).data
      },
      status=status.HTTP_200_OK
    )

