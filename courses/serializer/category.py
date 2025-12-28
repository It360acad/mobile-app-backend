

from courses.models.category import Category
from rest_framework import serializers
from users.serializer import UserSerializer
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
  """Serializer for the Category model"""

  created_by = UserSerializer(read_only=True)
  updated_by = UserSerializer(read_only=True)

  class Meta:
    model = Category
    fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'created_by', 'updated_by', 'courses_count']
    read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'courses_count']
    extra_kwargs = {
      'slug': {'required': False},
      'created_by': {'write_only': True},
      'updated_by': {'write_only': True},
    }


    def validate_name(self, value):
      if not value.strip():
        raise serializers.ValidationError('Category name cannot be empty')
      return value.strip()

    def create(self, validated_data):
      """Auto-generate slug if not provided"""
      if 'slug' not in validated_data or not validated_data['slug']:
        validated_data['slug'] = slugify(validated_data['name'])

    # set created_by from the request usr 
      request = self.context.get('request') 
      if request and hasattr(request, 'user'):
        validated_data['created_by'] = request.user
      return super().create(validated_data)


    def update(self, instance, validated_data):
      """update category name and slug if provided"""
      if 'name' in validated_data and validated_data['name'] != instance.name:
        if 'slug' not in validated_data:
          validated_data['slug'] = slugify(validated_data['name'])

      request = self.context.get('request')
      if request and hasattr(request, 'user'):
        validated_data['updated_by'] = request.user
      return super().update(instance, validated_data)

class CategoryListSerializer(serializers.ModelSerializer):
  """Serializer for the Category model in list view"""

  class Meta:
    model = Category
    fields = ['id', 'name', 'slug', 'created_at', 'updated_at', 'created_by', 'updated_by', 'courses_count']
    read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 'courses_count']

  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['created_by'] = UserSerializer(instance.created_by).data
    data['updated_by'] = UserSerializer(instance.updated_by).data
    return data