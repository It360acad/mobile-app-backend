from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_nested import routers
from courses.views import CategoryViewSet, CourseViewSet, LessonViewSet, QuizViewSet, CourseEnrollmentViewSet, CertificateViewSet, CourseBookmarkViewSet, CourseReviewViewSet, QuizAttemptViewSet
from notification.views import NotificationPreferenceViewSet, NotificationViewSet
from users.views import StudentViewSet
from payments.views import PaymentViewSet, paystack_webhook

# Main router for top-level resources
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'students', StudentViewSet, basename='students')
router.register(r'certificates', CertificateViewSet, basename='certificates')
router.register(r'bookmarks', CourseBookmarkViewSet, basename='bookmarks')
router.register(r'reviews', CourseReviewViewSet, basename='reviews')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempts')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'payments', PaymentViewSet, basename='payments')

# Nested router: courses/{course_id}/enrollments
courses_router = routers.NestedDefaultRouter(router, r'courses', lookup='course')
courses_router.register(r'lessons', LessonViewSet, basename='course-lessons')
courses_router.register(r'enrollments', CourseEnrollmentViewSet, basename='course-enrollments')
courses_router.register(r'reviews', CourseReviewViewSet, basename='course-reviews')

# Nested router: students/{student_pk}/courses (mapped to enrollments)
students_router = routers.NestedDefaultRouter(router, r'students', lookup='student')
students_router.register(r'courses', CourseEnrollmentViewSet, basename='student-courses')
students_router.register(r'bookmarks', CourseBookmarkViewSet, basename='student-bookmarks')

# Nested router: lessons/{lesson_id}/quizzes
lessons_router = routers.NestedDefaultRouter(courses_router, r'lessons', lookup='lesson')
lessons_router.register(r'quizzes', QuizViewSet, basename='lesson-quizzes')

# Nested router: quizzes/{quiz_id}/attempts
quizzes_router = routers.NestedDefaultRouter(lessons_router, r'quizzes', lookup='quiz')
quizzes_router.register(r'attempts', QuizAttemptViewSet, basename='quiz-attempts')

# Nested router: notifications
notification_router = routers.NestedDefaultRouter(router, r'notifications', lookup='notification')
notification_router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preferences')



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
    path('api/', include(students_router.urls)),
    path('api/', include(lessons_router.urls)),
    path('api/', include(notification_router.urls)),

    # Note: WebSocket routes are handled by ASGI (see it360acad_backend/asgi.py)
    # WebSocket endpoint: ws://domain/ws/chat/<parent_id>/

    # Payments
    path('api/webhook/paystack/', paystack_webhook, name='paystack_webhook'),
    
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
# 
# Quizzes (nested under lessons):
# GET    /api/courses/{course_id}/lessons/{lesson_id}/quizzes/           - List all quizzes in lesson
# POST   /api/courses/{course_id}/lessons/{lesson_id}/quizzes/           - Create quiz in lesson
# GET    /api/courses/{course_id}/lessons/{lesson_id}/quizzes/{id}/      - Get specific quiz
# PUT    /api/courses/{course_id}/lessons/{lesson_id}/quizzes/{id}/      - Update quiz
# DELETE /api/courses/{course_id}/lessons/{lesson_id}/quizzes/{id}/      - Delete quiz