import logging
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from users.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserDetailSerializer, UserUpdateSerializer, LinkChildSerializer
from users.cache import (
    get_cached_user_list,
    set_cached_user_list,
    invalidate_user_list_cache,
    get_cached_user,
    set_cached_user,
    invalidate_user_cache
)

# Get the logger named 'users'
logger = logging.getLogger('users')


# User List View
@extend_schema(
  tags=['Users'],
  summary="List Users",
  description="Get a list of all users in the database (cached in Redis).",
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
    
    # Try to get from cache first
    cached_data = get_cached_user_list()
    if cached_data is not None:
      logger.debug("Returning cached user list")
      return Response(cached_data, status=status.HTTP_200_OK)
    
    # Cache miss - get from database
    response = super().get(request, *args, **kwargs)
    
    # Cache the response data
    if response.status_code == 200 and hasattr(response, 'data'):
      set_cached_user_list(response.data)
      logger.debug("Cached user list")
    
    return response


# User Retrieve View
@extend_schema(
  tags=['Users'],
  summary="Retrieve User",
  description="Get a specific user by their primary key (pk) (cached in Redis).",
)
class UserRetrieveView(RetrieveAPIView):
  queryset = User.objects.all()
  serializer_class = UserDetailSerializer
  permission_classes = [IsAuthenticated]

  def get(self, request, *args, **kwargs):
    # Try to get from cache first
    user_id = kwargs.get('pk')
    if user_id:
      cached_data = get_cached_user(user_id)
      if cached_data is not None:
        logger.debug(f"Returning cached user {user_id}")
        return Response(cached_data, status=status.HTTP_200_OK)
    
    # Cache miss - get from database
    response = super().get(request, *args, **kwargs)
    
    # Cache the response data
    if response.status_code == 200 and hasattr(response, 'data') and user_id:
      set_cached_user(user_id, response.data)
      logger.debug(f"Cached user {user_id}")
    
    return response


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

  def put(self, request, *args, **kwargs):
    response = super().put(request, *args, **kwargs)
    # Invalidate cache after update
    user_id = kwargs.get('pk')
    if user_id:
      invalidate_user_cache(user_id)
      invalidate_user_list_cache()  # Also invalidate list cache
      logger.info(f"Invalidated cache for updated user {user_id}")
    return response

  def patch(self, request, *args, **kwargs):
    response = super().patch(request, *args, **kwargs)
    # Invalidate cache after update
    user_id = kwargs.get('pk')
    if user_id:
      invalidate_user_cache(user_id)
      invalidate_user_list_cache()  # Also invalidate list cache
      logger.info(f"Invalidated cache for updated user {user_id}")
    return response


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

