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


# Resend OTP Serializer
class ResendOTPSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  otp_type = serializers.ChoiceField(
    choices=[('registration', 'Registration'), ('password_reset', 'Password Reset')],
    required=False,
    default='registration',
    help_text="Type of OTP to resend: 'registration' or 'password_reset'"
  )

  def validate_email(self, value):
    """Check if user with this email exists"""
    try:
      User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User with this email does not exist")
    return value


# Forget Password Serializer - Request OTP for password reset
class ForgetPasswordSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")

  def validate_email(self, value):
    """Check if user with this email exists"""
    try:
      User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User with this email does not exist")
    return value


# Reset Password Serializer - Reset password with OTP verification
class ResetPasswordSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  code = serializers.CharField(required=True, min_length=6, max_length=6, help_text="6-digit OTP code")
  new_password = serializers.CharField(required=True, min_length=8, write_only=True, help_text="New password")
  confirm_password = serializers.CharField(required=True, min_length=8, write_only=True, help_text="Confirm new password")

  def validate(self, attrs):
    if attrs['new_password'] != attrs['confirm_password']:
      raise serializers.ValidationError("Passwords do not match")
    return attrs

  def validate_email(self, value):
    """Check if user with this email exists"""
    try:
      User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User with this email does not exist")
    return value

  
  #  Delete Account Serializer
class DeleteAccountSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="User password")
  confirm_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="Confirm user password")

  def validate(self, attrs):
    if attrs['password'] != attrs['confirm_password']:
      raise serializers.ValidationError("Passwords do not match")
    return attrs

  def validate_email(self, value):
    """Check if user with this email exists"""
    try:
      User.objects.get(email=value)
    except User.DoesNotExist:
      raise serializers.ValidationError("User with this email does not exist")
    return value

  def delete_account(self, request):
    """Delete user account"""
    user = self.context['request'].user
    email = user.email
    
    # Optional: Soft delete instead of hard delete
    # user.is_active = False
    # user.deleted_at = timezone.now()
    # user.save()
    
    # Hard delete
    user.delete()
    
    return {
        'message': 'Account deleted successfully',
        'email': email
    }
