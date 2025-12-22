from rest_framework import serializers
from users.models import User
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, required=False)
  username = serializers.CharField(required=False, allow_blank=True, allow_null=True)

  class Meta:
    model = User
    fields = ['id', 'email', 'first_name', 'last_name', 'role', 'username', 'password', 'date_joined']
    extra_kwargs = {
      'email': {'required': True},
      'role': {'required': True},
    }
  
  # Hash password before creating user
  def create(self, validated_data):
    password = validated_data.pop('password', None)
    if not password:
      raise serializers.ValidationError({'password': 'Password is required for registration'})
    validated_data['password'] = make_password(password)
    # Auto-generate username if not provided
    if 'username' not in validated_data or not validated_data.get('username'):
      email = validated_data.get('email', '')
      validated_data['username'] = email.split('@')[0] if email else 'user'
    validated_data['role'] = validated_data.get('role', 'student')
    return super().create(validated_data)

  def update(self, instance, validated_data):
    password = validated_data.pop('password', None)
    if password:
      instance.set_password(password)
    return super().update(instance, validated_data)

  
  def to_representation(self, instance):
    data = super().to_representation(instance)
    data['role'] = instance.role
    return data



