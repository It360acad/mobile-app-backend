from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view

from courses.models import Category
from courses.serializer.category import CategorySerializer, CategoryListSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'courses_count', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'  # Allow lookup by slug instead of ID
    
    def get_permissions(self):
        """
        - List and retrieve are public
        - Create, update, delete require admin
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action in ['create', 'update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def partial_update(self, request, *args, **kwargs):
        """Disable PATCH method"""
        return Response(
            {'error': 'PATCH method is not allowed. Use PUT for updates.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def perform_create(self, serializer):
        """Automatically set created_by and updated_by"""
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Automatically update updated_by"""
        serializer.save(updated_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Custom delete to check if category has courses
        """
        category = self.get_object()
        
        if category.courses_count > 0:
            return Response(
                {
                    'error': 'Cannot delete category with existing courses. '
                             'Please reassign or delete courses first.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)