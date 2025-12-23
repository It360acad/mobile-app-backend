from django.db import models
from django.utils import timezone
from django.conf import settings
import random
import string


class OTP(models.Model):
    """
    OTP model to store verification codes for user registration
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=6)  # 6-digit OTP code
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'code', 'is_used']),
        ]
    
    def __str__(self):
        return f"OTP for {self.user.email}: {self.code}"
    
    @staticmethod
    def generate_code():
        """Generate a 6-digit OTP code"""
        # TODO: For development, using fixed code. Change to random in production:
        # return ''.join(random.choices(string.digits, k=6))
        return '123456'
    
    @staticmethod
    def create_otp(user, expiry_minutes=10):
        """
        Create a new OTP for a user
        Args:
            user: User instance
            expiry_minutes: OTP expiry time in minutes (default 10)
        Returns:
            OTP instance
        """
        # Invalidate all previous unused OTPs for this user
        OTP.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new OTP
        code = OTP.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        
        otp = OTP.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        return otp
    
    def is_valid(self):
        """Check if OTP is still valid (not used and not expired)"""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def verify(self):
        """Mark OTP as used"""
        if self.is_valid():
            self.is_used = True
            self.save()
            return True
        return False
