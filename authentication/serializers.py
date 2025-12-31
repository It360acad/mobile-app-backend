from users.models import User
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
  password = serializers.CharField(required=False, write_only=True, style={'input_type': 'password'}, help_text="User password (required for self-deletion, optional for admin)")
  confirm_password = serializers.CharField(required=False, write_only=True, style={'input_type': 'password'}, help_text="Confirm user password (required for self-deletion, optional for admin)")

  def validate(self, attrs):
    request = self.context.get('request')
    current_user = request.user if request else None
    
    # If user is deleting their own account, password is required
    if current_user and current_user.email == attrs.get('email'):
      password = attrs.get('password')
      confirm_password = attrs.get('confirm_password')
      
      if not password or not confirm_password:
        raise serializers.ValidationError("Password and confirm password are required when deleting your own account")
      
      if password != confirm_password:
        raise serializers.ValidationError("Passwords do not match")
    
    # If admin is deleting another user's account, password is not required
    elif current_user and (current_user.is_superuser or current_user.role == 'admin'):
      # Admin can delete without password verification
      pass
    else:
      # Regular user trying to delete another account
      raise serializers.ValidationError("You can only delete your own account unless you are an admin")
    
    return attrs

  def validate_email(self, value):
    """Validate email - must exist and match logged-in user (unless admin)"""
    request = self.context.get('request')
    if not request or not request.user.is_authenticated:
      raise serializers.ValidationError("You must be logged in to delete an account")
    
    current_user = request.user
    
    # Admin can delete any user's account
    if current_user.is_superuser or current_user.role == 'admin':
      # Check if the email exists
      try:
        User.objects.get(email=value)
      except User.DoesNotExist:
        raise serializers.ValidationError("User with this email does not exist")
      return value
    
    # Regular user can only delete their own account
    if current_user.email != value:
      raise serializers.ValidationError("Email does not match your account email. You can only delete your own account.")
    
    return value

  def delete_account(self):
    """Delete user account - supports both self-deletion and admin deletion"""
    request = self.context['request']
    current_user = request.user
    email_to_delete = self.validated_data.get('email')
    
    # Get the user to delete
    if current_user.email == email_to_delete:
      # User is deleting their own account
      user_to_delete = current_user
      
      # Verify password before deletion
      password = self.validated_data.get('password')
      if not password:
        raise serializers.ValidationError({'password': 'Password is required to delete your account'})
      
      if not user_to_delete.check_password(password):
        raise serializers.ValidationError({'password': 'Invalid password'})
    else:
      # Admin is deleting another user's account
      if not (current_user.is_superuser or current_user.role == 'admin'):
        raise serializers.ValidationError("Only admins can delete other users' accounts")
      
      try:
        user_to_delete = User.objects.get(email=email_to_delete)
      except User.DoesNotExist:
        raise serializers.ValidationError({'email': 'User with this email does not exist'})
    
    deleted_email = user_to_delete.email
    
    # Optional: Soft delete instead of hard delete
    # user_to_delete.is_active = False
    # user_to_delete.deleted_at = timezone.now()
    # user_to_delete.save()
    
    # Hard delete
    user_to_delete.delete()
    
    return {
        'message': 'Account deleted successfully',
        'email': deleted_email,
        'deleted_by': 'admin' if (current_user.is_superuser or current_user.role == 'admin') and current_user.email != deleted_email else 'self'
    }
