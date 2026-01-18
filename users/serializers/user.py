from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from users.models import User, Profile, Student, Parent
from django.contrib.auth.hashers import make_password

# User Serializer
class UserSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, required=False)
  username = serializers.CharField(required=False, read_only=True)  # Auto-generated from email
  role = serializers.ChoiceField(choices=[('student', 'Student'), ('parent', 'Parent')], default='student')
  
  # Student fields
  student_id = serializers.CharField(required=False, write_only=True)
  current_class = serializers.CharField(required=False, write_only=True)
  current_school = serializers.CharField(required=False, write_only=True)
  
  # Parent fields
  parent_id = serializers.CharField(required=False, write_only=True)
  occupation = serializers.CharField(required=False, write_only=True)
  relationship_to_student = serializers.CharField(required=False, write_only=True)
  linking_code = serializers.CharField(required=False, write_only=True)

  class Meta:
    model = User
    fields = [
      'id', 'email', 'phone_number', 'first_name', 'last_name', 'role', 'username', 'password', 'date_joined',
      'student_id', 'current_class', 'current_school',
      'parent_id', 'occupation', 'relationship_to_student', 'linking_code'
    ]
    extra_kwargs = {
      'email': {'required': True},
      'phone_number': {'required': True},
    }
  
  def validate_role(self, value):
    """Ensure regular users can only be 'student' or 'parent'"""
    if value == 'admin':
      raise serializers.ValidationError("Regular users cannot have 'admin' role. Only superusers can be admins.")
    if value not in ['student', 'parent']:
      raise serializers.ValidationError("Role must be either 'student' or 'parent'.")
    return value
  
  # Hash password before creating user
  def create(self, validated_data):
    password = validated_data.pop('password', None)
    
    # Extract student/parent specific data
    student_data = {
      'student_id': validated_data.pop('student_id', None),
      'current_class': validated_data.pop('current_class', None),
      'current_school': validated_data.pop('current_school', None),
    }
    parent_data = {
      'parent_id': validated_data.pop('parent_id', None),
      'occupation': validated_data.pop('occupation', None),
      'relationship_to_student': validated_data.pop('relationship_to_student', None),
    }
    linking_code = validated_data.pop('linking_code', None)

    if not password:
      raise serializers.ValidationError({'password': 'Password is required for registration'})
    validated_data['password'] = make_password(password)
    
    # Always set username to email since USERNAME_FIELD is 'email'
    email = validated_data.get('email', '')
    if email:
      validated_data['username'] = email
    else:
      raise serializers.ValidationError({'email': 'Email is required'})
    
    role = validated_data.get('role', 'student')
    validated_data['is_verified'] = False
    validated_data['is_active'] = True
    
    user = super().create(validated_data)
    
    # Create Profile
    Profile.objects.create(user=user)
    
    # Create role-specific profile
    if role == 'student':
      Student.objects.create(user=user, **{k: v for k, v in student_data.items() if v is not None})
    elif role == 'parent':
      parent_profile = Parent.objects.create(user=user, **{k: v for k, v in parent_data.items() if v is not None})
      # Link child if code provided
      if linking_code:
        try:
          student = Student.objects.get(linking_code=linking_code)
          if not student.parent:
            student.parent = parent_profile
            student.save()
        except Student.DoesNotExist:
          # We might want to raise an error here, but for registration, 
          # maybe just ignore or handle it gracefully
          pass
      
    return user

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
      'last_login', 'address', 'city', 'state', 'zip_code', 
      'country', 'date_of_birth', 'gender'
    ]
    read_only_fields = ['id', 'date_joined', 'last_login']


# User Serializer with Profile (for list and retrieve)
class UserDetailSerializer(serializers.ModelSerializer):
  username = serializers.CharField(required=False, read_only=True)

  class Meta:
    model = User
    fields = [
      'id', 'email', 'phone_number', 'first_name', 'last_name', 'role', 'username', 
      'date_joined', 'is_verified'
    ]
    read_only_fields = ['id', 'username', 'date_joined', 'is_verified']


# User Update Serializer (for update operations)
class UserUpdateSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only=True, min_length=8, required=False)
  username = serializers.CharField(required=False, read_only=True)
  profile = ProfileSerializer(required=False)
  role = serializers.ChoiceField(choices=[('student', 'Student'), ('parent', 'Parent'), ('admin', 'Admin')], required=False)

  class Meta:
    model = User
    fields = [
      'id', 'email', 'first_name', 'last_name', 'role', 'username', 
      'password', 'date_joined', 'is_verified', 'profile'
    ]
    read_only_fields = ['id', 'username', 'date_joined', 'is_verified']

  def validate_role(self, value):
    """Ensure regular users can only be 'student' or 'parent'. Only superusers can be 'admin'."""
    # Allow admin role only if the user is already a superuser
    if value == 'admin':
      # Check if this is an update and the instance is a superuser
      if self.instance and not self.instance.is_superuser:
        raise serializers.ValidationError("Only superusers can have 'admin' role.")
    elif value not in ['student', 'parent']:
      raise serializers.ValidationError("Role must be either 'student' or 'parent'.")
    return value

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


class LinkChildSerializer(serializers.Serializer):
  linking_code = serializers.CharField(required=True)

  def validate_linking_code(self, value):
    try:
      student = Student.objects.get(linking_code=value)
    except Student.DoesNotExist:
      raise serializers.ValidationError("Invalid linking code.")
    
    if student.parent:
      raise serializers.ValidationError("This student is already linked to a parent.")
    
    return value

  def link_child(self, parent_user):
    linking_code = self.validated_data['linking_code']
    student = Student.objects.get(linking_code=linking_code)
    
    # Get the parent profile
    try:
      parent_profile = parent_user.parent_profile
    except AttributeError:
      raise serializers.ValidationError("User does not have a parent profile.")
    
    student.parent = parent_profile
    student.save()
    return student

