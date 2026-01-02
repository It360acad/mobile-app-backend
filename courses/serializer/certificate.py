from rest_framework import serializers
from courses.models.certificate import Certificate
from courses.serializer.course import CourseListSerializer

class CertificateSerializer(serializers.ModelSerializer):
    course_details = CourseListSerializer(source='course', read_only=True)
    
    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'course_details', 'certificate_id', 'issued_at', 'certificate_url']
        read_only_fields = ['id', 'issued_at']

