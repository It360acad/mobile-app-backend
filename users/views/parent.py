from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.models import Parent
from users.serializers import ParentSerializer

class ParentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

