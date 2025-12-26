from django.urls import path
from users.views import UserListView, UserRetrieveView, UserUpdateView

urlpatterns = [
  path('', UserListView.as_view(), name='user-list'),
  path('<int:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
  path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
]