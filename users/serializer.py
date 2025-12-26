from rest_framework import serializers
from users.models import User, Profile
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, required=False)
  username = serializers.CharField(required=False, read_only=True)  # Auto-generated from email

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
    
    # Always set username to email since USERNAME_FIELD is 'email'
    # This prevents username conflicts and ensures uniqueness
    email = validated_data.get('email', '')
    if email:
      validated_data['username'] = email  # Use email as username
    else:
      raise serializers.ValidationError({'email': 'Email is required'})
    
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


# Profile Serializer
class ProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = Profile
    fields = [
      'id', 'bio', 'date_joined', 
      'last_login', 'address', 'phone_number', 'city', 'state', 'zip_code', 
      'country', 'date_of_birth', 'gender'
    ]
    read_only_fields = ['id', 'date_joined', 'last_login']


# User Serializer with Profile (for list and retrieve)
class UserDetailSerializer(serializers.ModelSerializer):
  profile = ProfileSerializer(read_only=True)
  username = serializers.CharField(required=False, read_only=True)

  class Meta:
    model = User
    fields = [
      'id', 'email', 'first_name', 'last_name', 'role', 'username', 
      'date_joined', 'is_verified', 'profile'
    ]
    read_only_fields = ['id', 'username', 'date_joined', 'is_verified']


# User Update Serializer (for update operations)
class UserUpdateSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, required=False)
  username = serializers.CharField(required=False, read_only=True)
  profile = ProfileSerializer(required=False)

  class Meta:
    model = User
    fields = [
      'id', 'email', 'first_name', 'last_name', 'role', 'username', 
      'password', 'date_joined', 'is_verified', 'profile'
    ]
    read_only_fields = ['id', 'username', 'date_joined', 'is_verified']

  def update(self, instance, validated_data):
    password = validated_data.pop('password', None)
    profile_data = validated_data.pop('profile', None)
    
    # Update password if provided
    if password:
      instance.set_password(password)
    
    # Update user fields
    for attr, value in validated_data.items():
      setattr(instance, attr, value)
    instance.save()
    
    # Update profile if provided
    if profile_data:
      try:
        profile = Profile.objects.get(user=instance)
        # Profile exists, update it
        for attr, value in profile_data.items():
          setattr(profile, attr, value)
        profile.save()
      except Profile.DoesNotExist:
        # Profile doesn't exist, create it with all the provided data
        profile_data['user'] = instance
        Profile.objects.create(**profile_data)
    
    return instance

