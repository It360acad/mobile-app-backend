from rest_framework import serializers
from users.models import Student
from .user import UserDetailSerializer

class StudentSerializer(serializers.ModelSerializer):
    user_details = UserDetailSerializer(source='user', read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'user_details', 'student_id', 'current_class', 'current_school']
        read_only_fields = ['id']

