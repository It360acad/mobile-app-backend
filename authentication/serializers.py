from rest_framework import serializers

# Login Serializer
class LoginSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, help_text="User password")


# OTP Verification Serializer
class OTPVerificationSerializer(serializers.Serializer):
  email = serializers.EmailField(required=True, help_text="User email address")
  code = serializers.CharField(required=True, min_length=6, max_length=6, help_text="6-digit OTP code")

