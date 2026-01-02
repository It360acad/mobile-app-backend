from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.models import Student
from users.serializers import StudentSerializer

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

