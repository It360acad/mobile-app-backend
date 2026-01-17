import secrets
from django.db import models
from django.conf import settings



class Payment(models.Model):

  STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
  ]


  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
  amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='amount')
  email = models.EmailField(verbose_name='email')
  reference = models.CharField(max_length=100, verbose_name='reference')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='status')
  paystack_response = models.JSONField(null=True, blank=True, verbose_name='paystack response')
  metadata = models.JSONField(null=True, blank=True, verbose_name='metadata')
  webhook_event_id = models.CharField(max_length=100, null=True, blank=True, unique=True, verbose_name='webhook event id', help_text='Paystack event ID for idempotency')
  verified_via_webhook = models.BooleanField(default=False, verbose_name='verified via webhook', help_text='True if payment status was updated via webhook')
  created_at = models.DateTimeField(auto_now_add=True, verbose_name='created at')
  updated_at = models.DateTimeField(auto_now=True, verbose_name='updated at')

  def __str__(self):
    return f"Payment for {self.user.email} - {self.amount} {self.currency}"

  def get_amount(self):
    return self.amount * 100


  @staticmethod
  def generate_refrence():
    return f"PAY-{secrets.token_urlsafe(10)}"
