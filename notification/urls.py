from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notification.views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
    path('notification-preferences/', NotificationPreferenceViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'partial_update'
    }), name='notification-preferences'),
]