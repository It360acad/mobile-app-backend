from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema
from users.models import Parent, Student
from users.serializers import ParentSerializer
from users.serializers.parent_courses import ParentChildrenCoursesSerializer
from courses.models.enrollment import CourseEnrollment
import logging

logger = logging.getLogger('users')


class ParentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class ParentChildrenCoursesView(APIView):
    """
    View for parents to see all courses their children are enrolled in.
    Returns data grouped by child, showing each child's enrollments.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Parents'],
        summary="Get Children's Enrolled Courses",
        description="Get a list of all courses that the parent's children are enrolled in. "
                    "Data is grouped by child, showing each child's course enrollments with progress details.",
        responses={200: ParentChildrenCoursesSerializer}
    )
    def get(self, request):
        # Verify user is a parent
        if request.user.role != 'parent':
            return Response(
                {'error': 'Only parents can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            # Get parent profile
            parent_profile = request.user.parent_profile
            
            # Get all children (students) linked to this parent
            children = Student.objects.filter(parent=parent_profile).select_related('user').prefetch_related(
                'user__enrollments__course',
                'user__enrollments__course__category'
            )
            
            if not children.exists():
                return Response(
                    {
                        'parent_name': request.user.get_full_name(),
                        'parent_email': request.user.email,
                        'total_children': 0,
                        'children': [],
                        'total_enrollments': 0,
                        'total_active_enrollments': 0,
                        'total_completed_enrollments': 0,
                        'message': 'No children linked to this parent account.'
                    },
                    status=status.HTTP_200_OK
                )
            
            # Build response data
            children_data = []
            total_enrollments = 0
            total_active = 0
            total_completed = 0
            
            for child in children:
                # Get all enrollments for this child
                enrollments = CourseEnrollment.objects.filter(
                    user=child.user
                ).select_related('course', 'course__category').order_by('-enrolled_at')
                
                active_count = enrollments.filter(status='active').count()
                completed_count = enrollments.filter(status='completed').count()
                
                total_enrollments += enrollments.count()
                total_active += active_count
                total_completed += completed_count
                
                children_data.append({
                    'child': child.user,
                    'student_id': child.student_id or '',
                    'current_class': child.current_class or '',
                    'current_school': child.current_school or '',
                    'enrollments': enrollments,
                    'total_enrollments': enrollments.count(),
                    'active_enrollments': active_count,
                    'completed_enrollments': completed_count,
                })
            
            # Prepare response data
            response_data = {
                'parent_name': request.user.get_full_name(),
                'parent_email': request.user.email,
                'total_children': children.count(),
                'children': children_data,
                'total_enrollments': total_enrollments,
                'total_active_enrollments': total_active,
                'total_completed_enrollments': total_completed,
            }
            
            # Serialize the response
            serializer = ParentChildrenCoursesSerializer(response_data)
            
            logger.info(
                f"Parent {request.user.email} retrieved children's courses. "
                f"Children: {children.count()}, Total enrollments: {total_enrollments}"
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Parent.DoesNotExist:
            return Response(
                {'error': 'Parent profile not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving parent children courses: {str(e)}")
            return Response(
                {'error': 'An error occurred while retrieving children\'s courses.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

