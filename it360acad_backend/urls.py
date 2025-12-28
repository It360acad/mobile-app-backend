from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_nested import routers

from courses.views import CategoryViewSet, CourseViewSet, LessonViewSet

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'courses', CourseViewSet, basename='courses')

# Nested router: courses/{course_id}/lessons
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'lessons', LessonViewSet, basename='course-lessons')

# You can also add more nested routes:
# courses_router.register(r'quizzes', QuizViewSet, basename='course-quizzes')
# courses_router.register(r'enrollments', EnrollmentViewSet, basename='course-enrollments')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Apps
    path('api/auth/', include('authentication.urls')),
    path('api/users/', include('users.urls')),

    # Main routes
    path('api/', include(router.urls)),
    
    # Nested routes
    path('api/', include(courses_router.urls)),
]

# This creates these endpoints:
# 
# Categories:
# GET    /api/categories/
# POST   /api/categories/
# GET    /api/categories/{slug}/
# PUT    /api/categories/{slug}/
# DELETE /api/categories/{slug}/
# 
# Courses:
# GET    /api/courses/
# POST   /api/courses/
# GET    /api/courses/{id}/
# PUT    /api/courses/{id}/
# DELETE /api/courses/{id}/
# 
# Lessons (nested under courses):
# GET    /api/courses/{course_id}/lessons/           - List all lessons in course
# POST   /api/courses/{course_id}/lessons/           - Create lesson in course
# GET    /api/courses/{course_id}/lessons/{id}/      - Get specific lesson
# PUT    /api/courses/{course_id}/lessons/{id}/      - Update lesson
# DELETE /api/courses/{course_id}/lessons/{id}/      - Delete lesson