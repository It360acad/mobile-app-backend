from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from users.models import User
from users.serializer import UserSerializer
from authentication.serializers import LoginSerializer


class UserRegisterView(CreateAPIView):
  queryset = User.objects.all() # QuerySet to get all users
  serializer_class = UserSerializer # Serializer to serialize the user data
  permission_classes = [AllowAny] # Permission classes to allow any user to register 


  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = serializer.save()

    # Generate tokens
    refresh = RefreshToken.for_user(user)

    return Response({
      'message': 'User registered successfully',
      'user': UserSerializer(user).data,
      'tokens': {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
      }
    }, status=status.HTTP_201_CREATED)


# Custom Login View
class UserLoginView(APIView):
  permission_classes = [AllowAny]
  serializer_class = LoginSerializer

  def post(self, request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')

    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is None:
      return Response(
        {'error': 'Invalid email or password'},
        status=status.HTTP_401_UNAUTHORIZED
      )

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
      'user': UserSerializer(user).data,
      'tokens': {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
      }
    }, status=status.HTTP_200_OK)
