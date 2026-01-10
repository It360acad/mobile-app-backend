from django.urls import path
from users.views import (
    UserListView, 
    UserRetrieveView, 
    UserUpdateView, 
    LinkChildView,
    ParentChildrenCoursesView
)

urlpatterns = [
  path('', UserListView.as_view(), name='user-list'),
  path('link-child/', LinkChildView.as_view(), name='link-child'),
  path('parent/children-courses/', ParentChildrenCoursesView.as_view(), name='parent-children-courses'),
  path('<int:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
  path('<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
]