from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from courses.models.certificate import Certificate
from courses.serializer.certificate import CertificateSerializer

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing certificates.
    Certificates are created by the system upon course completion.
    """
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Certificate.objects.all()
        return Certificate.objects.filter(user=user)

