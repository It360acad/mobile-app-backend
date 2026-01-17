from rest_framework import serializers
from  .models import Payment

class PaymentInitSerializer(serializers.Serializer):
  amount = serializers.DecimalField(
    max_digits=10, 
    decimal_places=2,
    help_text="Payment amount (e.g., 59741.60)"
  )
  email = serializers.EmailField(
    help_text="Email address of the payer"
  )
  metadata = serializers.JSONField(
    required=False,
    help_text='''
    Optional JSON object for additional payment context.
    
    Example:
    {
      "course_id": "123",
      "student_id": "456",
      "purpose": "course_purchase",
      "description": "Payment for Python Course"
    }
    
    Common fields:
    - course_id: ID of the course being purchased
    - student_id: ID of the student enrolling
    - purpose: Type of payment (e.g., "course_purchase", "subscription")
    - description: Human-readable description
    
    Note: All metadata values should be strings (Paystack requirement).
    '''
  )

  def validate_amount(self, value):
    if value <= 0:
      raise serializers.ValidationError("Amount must be greater than 0")
    return value

  def validate_email(self, value):
    if not value:
      raise serializers.ValidationError("Email is required")
    return value

  def validate_payer(self, value):
    if not value.role == 'parent':
      raise serializers.ValidationError("Only parents can pay for courses")
    return value

class PaymentSerializer(serializers.ModelSerializer):
  class Meta:
    model = Payment
    fields = ['id', 'amount', 'email', 'reference', 'metadata', 'status', 'created_at', 'updated_at']
    read_only_fields = ['id', 'created_at', 'updated_at', 'reference', 'status']


class PaymentVerifySerializer(serializers.Serializer):
  reference = serializers.CharField(required=True)

  def validate_reference(self, value):
    if not Payment.objects.filter(reference=value).exists():
      raise serializers.ValidationError("Invalid reference")
    return value
