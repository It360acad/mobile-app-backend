from django.urls import path
from authentication.views import UserRegisterView, UserLoginView, CustomTokenRefreshView, OTPVerificationView, UserLogoutView, UserForgetPasswordView

urlpatterns = [ 
  path('register/', UserRegisterView.as_view(), name='auth-register'),
  path('verify-otp/', OTPVerificationView.as_view(), name='auth-verify-otp'),
  path('login/', UserLoginView.as_view(), name='auth-login'),
  path('forget-password/', UserForgetPasswordView.as_view(), name='auth-forget-password'),
  path('logout/', UserLogoutView.as_view(), name='auth-logout'),
  path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]

