from django.contrib import admin
from .models import Payment

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
  list_display = ('user', 'amount', 'status', 'reference', 'paystack_response')
  list_filter = ('status', 'created_at', 'updated_at')