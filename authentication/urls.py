from django.urls import path
from authentication.views import UserDeleteAccountView, UserRegisterView, UserLoginView, CustomTokenRefreshView, OTPVerificationView, UserLogoutView, UserForgetPasswordView, UserResetPasswordView, UserEmailExistsView, UserResendOtpView, UserProfileView

urlpatterns = [ 
  path('register/', UserRegisterView.as_view(), name='auth-register'),
  path('verify-otp/', OTPVerificationView.as_view(), name='auth-verify-otp'),
  path('resend-otp/', UserResendOtpView.as_view(), name='auth-resend-otp'),
  path('login/', UserLoginView.as_view(), name='auth-login'),
  path('forget-password/', UserForgetPasswordView.as_view(), name='auth-forget-password'), # forget password view
  path('reset-password/', UserResetPasswordView.as_view(), name='auth-reset-password'), # reset password view
  path('check-email-exists/', UserEmailExistsView.as_view(), name='auth-check-email-exists'),
  path('delete-account/', UserDeleteAccountView.as_view(), name='auth-delete-account'),
  path('logout/', UserLogoutView.as_view(), name='auth-logout'),
  path('me/', UserProfileView.as_view(), name='user-profile'),
  path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]

