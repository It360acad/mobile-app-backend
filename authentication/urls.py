from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import UserRegisterView, UserLoginView

urlpatterns = [
  path('register/', UserRegisterView.as_view(), name='auth-register'),
  path('login/', UserLoginView.as_view(), name='auth-login'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

