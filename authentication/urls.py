from django.urls import path
from authentication.views import UserRegisterView, UserLoginView, CustomTokenRefreshView, OTPVerificationView

urlpatterns = [
  path('register/', UserRegisterView.as_view(), name='auth-register'),
  path('verify-otp/', OTPVerificationView.as_view(), name='auth-verify-otp'),
  path('login/', UserLoginView.as_view(), name='auth-login'),
  path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]

