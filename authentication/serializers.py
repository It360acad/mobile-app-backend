from django.contrib.auth.models import User
from rest_framework import serializers

# Login Serializer
class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="User password")


# OTP Verification Serializer
class OTPVerificationSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  code = serializers.CharField(required=True, min_length=6, max_length=6, help_text="6-digit OTP code")


# Forget Password Serializser
class ForgetPasswordSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  new_password = serializers.CharField(required=True, min_length=8, help_text="New password")
  confirm_password = serializers.CharField(required=True, min_length=8, help_text="Confirm new password")

  def validate(self, attrs):
    if attrs['new_password'] != attrs['confirm_password']:
      raise serializers.ValidationError("Passwords do not match")
    return attrs

  def validate_email(self, value):
    """check if user with this email exists"""
    try:
      User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User with this email does not exist")
    return value

  def save(self, validated_data):
    
    # user = User.objects.create_user( # this is user to create a new user. we are not using this because we are not creating a new user. we are resetting the password of an existing user.
    #   email=validated_data['email'],
    #   username=validated_data['email'],
    #   password=validated_data['new_password']
    # )
    # return user

    email = self.validated_data.get('email')
    new_password = self.validated_data.get('new_password')

    user = User.objects.get(email=email)
    user.set_password(new_password) # hash the password
    user.save()
    return user

  def to_representation(self, instance):
    return {
      'email': instance.email,
      'message': 'Password reset successfully',
    }