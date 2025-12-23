from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from users.models import User
from users.serializer import UserSerializer
from authentication.serializers import LoginSerializer, OTPVerificationSerializer
from authentication.models import OTP


@extend_schema(
  tags=['Authentication'],
  summary="User Registration",
  description="Register a new user. An OTP will be sent to the user's email for verification.",
)
class UserRegisterView(CreateAPIView):
  queryset = User.objects.all() # QuerySet to get all users
  serializer_class = UserSerializer # Serializer to serialize the user data
  permission_classes = [AllowAny] # Permission classes to allow any user to register 


  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Create user but set is_verified to False initially
    user = serializer.save()
    user.is_verified = False
    user.is_active = True  # User can login but needs to verify email
    user.save()

    # Generate and send OTP
    otp = OTP.create_otp(user, expiry_minutes=10)
    
    # TODO: Send OTP via email (we'll implement this later)
    # For now, we'll return it in the response (remove this in production!)
    print(f"OTP for {user.email}: {otp.code}")  # Remove in production!

    return Response({
      'message': 'User registered successfully. Please check your email for OTP verification code.',
      'user': {
        'id': user.id,
        'email': user.email,
      },
      # Remove this in production - only for development/testing
      'otp_code': otp.code if request.data.get('debug', False) else None,
    }, status=status.HTTP_201_CREATED)


# Custom Login View
@extend_schema(
  request=LoginSerializer,
  tags=['Authentication'],
  summary="User Login",
  description="Authenticate a user with email and password. Returns user data and JWT tokens.",
)
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


# OTP Verification View
@extend_schema(
  request=OTPVerificationSerializer,
  tags=['Authentication'],
  summary="Verify OTP",
  description="Verify OTP code sent to user's email. Returns JWT tokens upon successful verification.",
)
class OTPVerificationView(APIView):
  permission_classes = [AllowAny]
  serializer_class = OTPVerificationSerializer

  def post(self, request):
    serializer = OTPVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data.get('email')
    code = serializer.validated_data.get('code')
    
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      return Response(
        {'error': 'User with this email does not exist'},
        status=status.HTTP_404_NOT_FOUND
      )
    
    # Find the most recent unused OTP for this user
    otp = OTP.objects.filter(
      user=user,
      code=code,
      is_used=False
    ).order_by('-created_at').first()
    
    if not otp:
      return Response(
        {'error': 'Invalid or expired OTP code'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    # Check if OTP is valid (not expired)
    if not otp.is_valid():
      return Response(
        {'error': 'OTP code has expired. Please request a new one.'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    # Verify the OTP
    if otp.verify():
      # Mark user as verified
      user.is_verified = True
      user.save()
      
      # Generate tokens
      refresh = RefreshToken.for_user(user)
      
      return Response({
        'message': 'Email verified successfully',
        'user': UserSerializer(user).data,
        'tokens': {
          'refresh': str(refresh),
          'access': str(refresh.access_token),
        }
      }, status=status.HTTP_200_OK)
    else:
      return Response(
        {'error': 'Failed to verify OTP'},
        status=status.HTTP_400_BAD_REQUEST
      )


# Custom Token Refresh View with Authentication tag
@extend_schema(
  tags=['Authentication'],
  summary="Refresh Token",
  description="Refresh JWT access token using refresh token.",
)
class CustomTokenRefreshView(TokenRefreshView):
  pass
