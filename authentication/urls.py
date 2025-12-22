from django.urls import path
from authentication.views import UserRegisterView, UserLoginView, CustomTokenRefreshView

urlpatterns = [
  path('register/', UserRegisterView.as_view(), name='auth-register'),
  path('login/', UserLoginView.as_view(), name='auth-login'),
  path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
]

