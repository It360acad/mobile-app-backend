from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from users.models import User
from users.serializer import UserSerializer
from authentication.serializers import ForgetPasswordSerializer, ResetPasswordSerializer, LoginSerializer, OTPVerificationSerializer
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
    # For now, using fixed OTP code: 123456
    # print(f"OTP for {user.email}: {otp.code}")  # Development only

    return Response({
      'message': 'User registered successfully. Please check your email for OTP verification code.',
      'user': {
        'id': user.id,
        'email': user.email,
      },
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


# Forget Password View - Request OTP for password reset
@extend_schema(
  request=ForgetPasswordSerializer,
  tags=['Authentication'],
  summary="Forget Password",
  description="Request a password reset OTP. An OTP will be sent to the user's email.",
)
class UserForgetPasswordView(APIView):
  permission_classes = [AllowAny]
  serializer_class = ForgetPasswordSerializer

  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data.get('email')
    
    try:
      user = User.objects.get(email=email)
    except User.DoesNotExist:
      return Response(
        {'error': 'User with this email does not exist'},
        status=status.HTTP_404_NOT_FOUND
      )
    
    # Generate and send OTP for password reset
    otp = OTP.create_otp(user, expiry_minutes=15)  # 15 minutes expiry for password reset
    
    # TODO: Send OTP via email (we'll implement this later)
    # For now, using fixed OTP code: 123456
    # print(f"Password Reset OTP for {user.email}: {otp.code}")  # Development only
    
    return Response(
      {
        'message': 'Password reset OTP has been sent to your email. Please check your inbox.',
        'email': user.email
      },
      status=status.HTTP_200_OK
    )


# Reset Password View - Reset password with OTP verification
@extend_schema(
  request=ResetPasswordSerializer,
  tags=['Authentication'],
  summary="Reset Password",
  description="Reset a user's password using the OTP code sent to their email.",
)
class UserResetPasswordView(APIView):
  permission_classes = [AllowAny]
  serializer_class = ResetPasswordSerializer

  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    email = serializer.validated_data.get('email')
    code = serializer.validated_data.get('code')
    new_password = serializer.validated_data.get('new_password')
    
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
      # Reset the password
      user.set_password(new_password)
      user.save()
      
      return Response(
        {
          'message': 'Password has been reset successfully. You can now login with your new password.',
          'email': user.email
        },
        status=status.HTTP_200_OK
      )
    else:
      return Response(
        {'error': 'Failed to verify OTP'},
        status=status.HTTP_400_BAD_REQUEST
      )


# Logout View
@extend_schema(
  tags=['Authentication'],
  summary="Logout User",
  description="Logout a user. Invalidates the refresh token.",
)
class UserLogoutView(APIView):
  permission_classes = [IsAuthenticated]
  serializer_class = None

  def post(self, request):
    refresh_token = request.data.get('refresh')
    if refresh_token:
      try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
          {'message': 'Logged out successfully'},
          status=status.HTTP_200_OK
        )
      except Exception as e:
        return Response(
          {'error': str(e)},
          status=status.HTTP_400_BAD_REQUEST
        )
    else:
      return Response(
        {'error': 'Refresh token is required'},
        status=status.HTTP_400_BAD_REQUEST
      )


# TODOS: add rate limiting to the email exists view for security when scalling to production
#  Email Exist View
@extend_schema(
  tags=['Authentication'],
  summary="Check if email exists in the database",
  description="Check if email exists in the database.",
)
class UserEmailExistsView(APIView):
  permission_classes = [AllowAny]
  serializer_class = None

  def get(self, request):
    email = request.query_params.get('email') # get the email from the query params
    if User.objects.filter(email=email).exists(): # check if the email exists in the database
      return Response ({'exists': True}, status=status.HTTP_200_OK) # return True 
    else: # if the email does not exist in the database
      return Response({'exists': False}, status=status.HTTP_200_OK) # return False

# Custom Token Refresh View with Authentication tag
@extend_schema(
  tags=['Authentication'],
  summary="Refresh Token",
  description="Refresh JWT access token using refresh token.",
)
class CustomTokenRefreshView(TokenRefreshView):
  pass
