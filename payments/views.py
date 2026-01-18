# views.py
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiParameter
import hmac
import hashlib
import json

# Get logger for payments
logger = logging.getLogger('payments')

from .models import Payment
from .serializers import (
    PaymentInitSerializer, 
    PaymentSerializer, 
    PaymentVerifySerializer
)
from .services import PaystackService

@extend_schema_view(
    list=extend_schema(
        summary='List Payments',
        description='Get a list of all payments for the authenticated user. Staff users can see all payments.',
        tags=['Payments']
    ),
    retrieve=extend_schema(
        summary='Get Payment Details',
        description='Retrieve details of a specific payment by ID.',
        tags=['Payments']
    ),
    create=extend_schema(
        summary='Create Payment',
        description='Create a new payment record. Note: Use the initialize endpoint to start a payment.',
        tags=['Payments']
    ),
    update=extend_schema(
        summary='Update Payment',
        description='Update a payment record.',
        tags=['Payments']
    ),
    destroy=extend_schema(
        summary='Delete Payment',
        description='Delete a payment record.',
        tags=['Payments']
    ),
)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments by user"""
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary='Initialize Payment',
        description='''
        Initialize a payment transaction with Paystack.
        
        This endpoint:
        1. Creates a payment record in the database
        2. Initializes the payment with Paystack
        3. Returns an authorization URL for the user to complete payment
        
        **Important:** After payment, the status is updated via webhook, not client-side.
        
        **Request Body:**
        - `amount`: Payment amount (decimal, e.g., 59741.60)
        - `email`: Payer's email address
        - `metadata`: (Optional) JSON object with additional context
        
        **Metadata Examples:**
        ```json
        {
          "course_id": "123",
          "student_id": "456",
          "purpose": "course_purchase",
          "description": "Payment for Python Course Bundle"
        }
        ```
        
        Or for multiple courses:
        ```json
        {
          "course_ids": ["123", "124", "125"],
          "student_id": "456",
          "purpose": "course_purchase"
        }
        ```
        
        **Note:** Metadata is optional. If not provided, use `null` or omit the field.
        ''',
        request={
            'application/json': {
                'type': 'object',
                'required': ['amount', 'email'],
                'properties': {
                    'amount': {
                        'type': 'number',
                        'format': 'decimal',
                        'description': 'Payment amount',
                        'example': 59741.60
                    },
                    'email': {
                        'type': 'string',
                        'format': 'email',
                        'description': 'Payer email address',
                        'example': 'user@example.com'
                    },
                    'metadata': {
                        'type': 'object',
                        'description': 'Optional JSON object for additional payment context. All values must be strings.',
                        'required': False,
                        'properties': {
                            'course_id': {
                                'type': 'string',
                                'description': 'ID of the course being purchased',
                                'example': '123'
                            },
                            'student_id': {
                                'type': 'string',
                                'description': 'ID of the student enrolling',
                                'example': '456'
                            },
                            'purpose': {
                                'type': 'string',
                                'description': 'Type of payment (e.g., course_purchase, subscription)',
                                'example': 'course_purchase'
                            },
                            'description': {
                                'type': 'string',
                                'description': 'Human-readable description of the payment',
                                'example': 'Payment for Python Course Bundle'
                            }
                        },
                        'example': {
                            'course_id': '123',
                            'student_id': '456',
                            'purpose': 'course_purchase',
                            'description': 'Payment for Python Course Bundle'
                        }
                    }
                },
                'example': {
                    'amount': 59741.60,
                    'email': 'user@example.com',
                    'metadata': {
                        'course_id': '123',
                        'student_id': '456',
                        'purpose': 'course_purchase',
                        'description': 'Payment for Python Course Bundle'
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description='Payment initialized successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'},
                        'message': {'type': 'string', 'example': 'Payment initialized'},
                        'data': {
                            'type': 'object',
                            'properties': {
                                'authorization_url': {'type': 'string', 'format': 'uri', 'description': 'URL to redirect user for payment'},
                                'access_code': {'type': 'string', 'description': 'Paystack access code'},
                                'reference': {'type': 'string', 'description': 'Payment reference for tracking'}
                            }
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description='Invalid request data or payment initialization failed',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'error'},
                        'message': {'type': 'string'}
                    }
                }
            )
        },
        tags=['Payments']
    )
    @action(detail=False, methods=['post'])
    def initialize(self, request):
        """Initialize a payment"""
        serializer = PaymentInitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get validated data
        amount = serializer.validated_data['amount']
        email = serializer.validated_data['email']
        metadata = serializer.validated_data.get('metadata', {})
        
        # Generate reference
        reference = Payment.generate_reference()
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            amount=amount,
            email=email,
            reference=reference,
            status='pending',
            metadata=metadata
        )
        
        # Initialize with Paystack
        paystack = PaystackService()
        callback_url = request.build_absolute_uri('/api/payments/callback/')
        
        # Ensure HTTPS in production (Paystack requires HTTPS for callbacks)
        if not settings.DEBUG and not callback_url.startswith('https://'):
            # Force HTTPS in production
            callback_url = callback_url.replace('http://', 'https://', 1)
            logger.warning(
                f"Callback URL was HTTP, forced to HTTPS: {callback_url}",
                extra={'user_id': request.user.id if request.user.is_authenticated else 'Anonymous', 'tenant_id': 'N/A'}
            )
        
        response = paystack.initialize_payment(
            email=email,
            amount=float(amount),
            reference=reference,
            callback_url=callback_url,
            metadata=metadata
        )
        
        if response.get('status'):
            return Response({
                'status': 'success',
                'message': 'Payment initialized',
                'data': {
                    'authorization_url': response['data']['authorization_url'],
                    'access_code': response['data']['access_code'],
                    'reference': reference
                }
            }, status=status.HTTP_200_OK)
        else:
            payment.delete()
            return Response({
                'status': 'error',
                'message': response.get('message', 'Payment initialization failed')
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary='Verify Payment Status',
        description='''
        Check the current status of a payment by reference.
        
        **Important:** This is a READ-ONLY endpoint. Payment status is ONLY updated via webhook for security.
        This endpoint only returns the current status from the database.
        
        **Security Note:** Never trust client-side verification. Always verify payments server-side via webhook.
        ''',
        request=PaymentVerifySerializer,
        responses={
            200: OpenApiResponse(
                description='Payment status retrieved successfully',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'},
                        'message': {'type': 'string', 'example': 'Payment status retrieved'},
                        'data': {
                            'type': 'object',
                            'properties': {
                                'reference': {'type': 'string'},
                                'status': {'type': 'string', 'enum': ['pending', 'completed', 'failed']},
                                'verified_via_webhook': {'type': 'boolean'},
                                'amount': {'type': 'string'},
                                'email': {'type': 'string'},
                                'created_at': {'type': 'string', 'format': 'date-time'},
                                'updated_at': {'type': 'string', 'format': 'date-time'}
                            }
                        }
                    }
                }
            ),
            404: OpenApiResponse(
                description='Payment not found',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'error'},
                        'message': {'type': 'string', 'example': 'Payment not found'}
                    }
                }
            )
        },
        tags=['Payments']
    )
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Check payment status (read-only)
        NOTE: Payment status is ONLY updated via webhook for security.
        This endpoint only returns the current status from our database.
        """
        serializer = PaymentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reference = serializer.validated_data['reference']
        
        try:
            payment = Payment.objects.get(reference=reference)
        except Payment.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Payment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Only return current status - do NOT update payment status
        # Payment status is only updated via webhook for security
        return Response({
            'status': 'success',
            'message': 'Payment status retrieved',
            'data': {
                'reference': payment.reference,
                'status': payment.status,
                'verified_via_webhook': payment.verified_via_webhook,
                'amount': str(payment.amount),
                'email': payment.email,
                'created_at': payment.created_at,
                'updated_at': payment.updated_at,
            }
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        summary='Payment Callback',
        description='''
        Handle Paystack redirect callback after payment.
        
        This is an optional endpoint that Paystack can redirect to after payment.
        It returns the payment reference for verification.
        
        **Note:** Payment status is still updated via webhook, not this callback.
        ''',
        parameters=[
            OpenApiParameter(
                'reference',
                str,
                OpenApiParameter.QUERY,
                required=True,
                description='Payment reference from Paystack'
            )
        ],
        responses={
            200: OpenApiResponse(
                description='Callback processed',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'success'},
                        'reference': {'type': 'string'},
                        'message': {'type': 'string'}
                    }
                }
            ),
            400: OpenApiResponse(
                description='No reference provided',
                response={
                    'type': 'object',
                    'properties': {
                        'status': {'type': 'string', 'example': 'error'},
                        'message': {'type': 'string', 'example': 'No reference provided'}
                    }
                }
            )
        },
        tags=['Payments']
    )
    @action(detail=False, methods=['get'])
    def callback(self, request):
        """Handle Paystack redirect callback (optional)"""
        reference = request.query_params.get('reference')
        
        if not reference:
            return Response({
                'status': 'error',
                'message': 'No reference provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # You can redirect to frontend with reference
        # For API, just return the reference
        return Response({
            'status': 'success',
            'reference': reference,
            'message': 'Please verify payment using the verify endpoint'
        })


@csrf_exempt
@extend_schema(
    summary='Paystack Webhook Endpoint',
    description='''
    Handle Paystack webhook events for payment notifications.
    
    **Security:**
    - All payment status updates MUST come through this webhook (server-side verification)
    - Webhook signature is validated using HMAC-SHA512
    - HTTPS is required in production
    
    **Supported Events:**
    - `charge.success` - Payment completed successfully
    - `charge.failed` - Payment failed
    - `transfer.success` - Transfer completed (if using payouts)
    - `transfer.failed` - Transfer failed (if using payouts)
    
    **Headers Required:**
    - `x-paystack-signature`: HMAC-SHA512 signature of the request body
    
    **Note:** This endpoint is called by Paystack, not by your frontend.
    ''',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'event': {
                    'type': 'string',
                    'description': 'Event type (e.g., charge.success, charge.failed)',
                    'example': 'charge.success'
                },
                'data': {
                    'type': 'object',
                    'description': 'Event data containing payment information',
                },
                'id': {
                    'type': 'string',
                    'description': 'Unique event ID for idempotency',
                    'example': 'evt_1234567890'
                }
            },
            'required': ['event', 'data', 'id']
        }
    },
    responses={
        200: OpenApiResponse(
            description='Webhook received and processed successfully',
            response={
                'type': 'string',
                'example': 'Webhook received and processed'
            }
        ),
        400: OpenApiResponse(
            description='Bad request (missing signature, invalid JSON, etc.)',
            response={
                'type': 'string',
                'example': 'Missing signature header'
            }
        ),
        401: OpenApiResponse(
            description='Invalid webhook signature',
            response={
                'type': 'string',
                'example': 'Invalid signature'
            }
        ),
        405: OpenApiResponse(
            description='Method not allowed (only POST is accepted)',
            response={
                'type': 'string',
                'example': 'Method not allowed'
            }
        ),
        500: OpenApiResponse(
            description='Server error processing webhook',
            response={
                'type': 'string',
                'example': 'Error processing webhook'
            }
        )
    },
    tags=['Payments'],
    operation_id='paystack_webhook'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def paystack_webhook(request):
    """
    Handle Paystack webhook events
    This is the main endpoint for receiving payment notifications.
    All payment status updates MUST come through this webhook for security.
    """
    # Get client IP for security logging
    client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
    
    # Log incoming webhook request
    logger.info(
        f"Webhook request received from IP: {client_ip}",
        extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
    )
    
    # Validate HTTPS in production (Paystack requires HTTPS for webhooks)
    is_secure = request.is_secure() or request.META.get('HTTP_X_FORWARDED_PROTO') == 'https'
    
    if not settings.DEBUG and not is_secure:
        logger.error(
            f"Webhook request received over HTTP (not HTTPS) from IP: {client_ip}. "
            f"Paystack webhooks require HTTPS in production.",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse(
            'HTTPS required for webhook endpoint in production. Paystack webhooks require HTTPS.',
            status=400
        )
    
    if not is_secure:
        logger.warning(
            f"Webhook request received over HTTP (development mode) from IP: {client_ip}. "
            f"Note: Paystack webhooks will not work with HTTP in production.",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
    
    # Validate HTTP method
    if request.method != 'POST':
        logger.warning(
            f"Invalid HTTP method {request.method} from IP: {client_ip}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Method not allowed', status=405)
    
    # Get signature from header
    paystack_signature = request.headers.get('x-paystack-signature')
    
    if not paystack_signature:
        logger.error(
            f"Webhook request missing signature header from IP: {client_ip}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Missing signature header', status=400)
    
    # Validate secret key is configured
    if not hasattr(settings, 'PAYSTACK_SECRET_KEY') or not settings.PAYSTACK_SECRET_KEY:
        logger.critical(
            "PAYSTACK_SECRET_KEY is not configured in settings",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Server configuration error', status=500)
    
    # Get request body (must be raw bytes for signature verification)
    try:
        body = request.body
        if not body:
            logger.warning(
                f"Empty request body from IP: {client_ip}",
                extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
            )
            return HttpResponse('Empty request body', status=400)
    except Exception as e:
        logger.error(
            f"Error reading request body from IP: {client_ip}: {str(e)}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Error reading request body', status=400)
    
    # Compute HMAC signature
    try:
        computed_signature = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
            body,
            hashlib.sha512
        ).hexdigest()
    except Exception as e:
        logger.error(
            f"Error computing signature: {str(e)}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Signature computation error', status=500)
    
    # Verify signature using constant-time comparison (prevents timing attacks)
    if not hmac.compare_digest(computed_signature, paystack_signature):
        logger.warning(
            f"Invalid webhook signature from IP: {client_ip}. "
            f"Expected: {computed_signature[:20]}..., Received: {paystack_signature[:20]}...",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Invalid signature', status=401)
    
    # Signature is valid, proceed with processing
    logger.info(
        f"Webhook signature verified successfully from IP: {client_ip}",
        extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
    )
    
    # Parse and validate JSON payload
    try:
        payload = json.loads(body.decode('utf-8'))
    except json.JSONDecodeError as e:
        logger.error(
            f"Invalid JSON payload from IP: {client_ip}: {str(e)}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Invalid JSON payload', status=400)
    except UnicodeDecodeError as e:
        logger.error(
            f"Unicode decode error from IP: {client_ip}: {str(e)}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Invalid encoding', status=400)
    
    # Validate required payload fields
    event = payload.get('event')
    data = payload.get('data')
    event_id = payload.get('id')
    
    if not event:
        logger.warning(
            f"Webhook payload missing 'event' field from IP: {client_ip}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse("Missing 'event' field in payload", status=400)
    
    if not data:
        logger.warning(
            f"Webhook payload missing 'data' field from IP: {client_ip}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse("Missing 'data' field in payload", status=400)
    
    if not event_id:
        logger.warning(
            f"Webhook payload missing 'id' field (event_id) from IP: {client_ip}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse("Missing 'id' field in payload", status=400)
    
    # Log valid webhook event
    logger.info(
        f"Processing webhook event: {event} (ID: {event_id}) from IP: {client_ip}",
        extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
    )
    
    # Process webhook event
    try:
        # Handle different event types
        if event == 'charge.success':
            handle_successful_payment(data, event_id)
        elif event == 'charge.failed':
            handle_failed_payment(data, event_id)
        elif event == 'transfer.success':
            handle_successful_transfer(data, event_id)
        elif event == 'transfer.failed':
            handle_failed_transfer(data, event_id)
        else:
            logger.info(
                f"Unhandled webhook event type: {event} (ID: {event_id}) from IP: {client_ip}",
                extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
            )
            # Return 200 to acknowledge receipt even if we don't handle it
            return HttpResponse(f'Event {event} received but not handled', status=200)
        
        logger.info(
            f"Webhook event {event} (ID: {event_id}) processed successfully",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return HttpResponse('Webhook received and processed', status=200)
    
    except Exception as e:
        logger.error(
            f"Error processing webhook event {event} (ID: {event_id}) from IP: {client_ip}: {str(e)}",
            exc_info=True,
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        # Return 200 to prevent Paystack from retrying (we'll handle retries manually if needed)
        # Or return 500 if you want Paystack to retry
        return HttpResponse('Error processing webhook', status=500)


def handle_successful_payment(data, event_id):
    """
    Handle successful payment event
    Only updates payment status via webhook (server-side verification)
    """
    reference = data.get('reference')
    
    if not reference:
        logger.warning(
            f"No reference in payment data for event {event_id}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return
    
    try:
        payment = Payment.objects.get(reference=reference)
        
        # Idempotency check: if we've already processed this webhook event, skip
        if payment.webhook_event_id == event_id:
            logger.info(
                f"Webhook event {event_id} already processed for payment {reference} (idempotency)",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
            return
        
        # Only update if payment is still pending (prevent overwriting confirmed status)
        if payment.status == 'pending' or not payment.verified_via_webhook:
            payment.status = 'completed'  # Use 'completed' to match STATUS_CHOICES
            payment.paystack_response = data
            payment.webhook_event_id = event_id
            payment.verified_via_webhook = True
            payment.save()
            
            logger.info(
                f"Payment successful: {reference} (event: {event_id}) - Amount: {payment.amount}, User: {payment.user.id if payment.user else 'Anonymous'}",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
            
            # Add your business logic here
            # Examples:
            # - Send confirmation email
            # - Activate user subscription
            # - Update order status
            # - Grant access to premium features
            
        else:
            logger.info(
                f"Payment {reference} already has status {payment.status}, skipping update (event: {event_id})",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
        
    except Payment.DoesNotExist:
        logger.warning(
            f"Payment not found for reference: {reference} (event: {event_id})",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
    except Payment.MultipleObjectsReturned:
        logger.error(
            f"Multiple payments found with reference: {reference} (event: {event_id})",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )


def handle_failed_payment(data, event_id):
    """
    Handle failed payment event
    Only updates payment status via webhook (server-side verification)
    """
    reference = data.get('reference')
    
    if not reference:
        logger.warning(
            f"No reference in payment data for event {event_id}",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
        return
    
    try:
        payment = Payment.objects.get(reference=reference)
        
        # Idempotency check: if we've already processed this webhook event, skip
        if payment.webhook_event_id == event_id:
            logger.info(
                f"Webhook event {event_id} already processed for payment {reference} (idempotency)",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
            return
        
        # Only update if payment is still pending (prevent overwriting confirmed status)
        if payment.status == 'pending' or not payment.verified_via_webhook:
            payment.status = 'failed'
            payment.paystack_response = data
            payment.webhook_event_id = event_id
            payment.verified_via_webhook = True
            payment.save()
            
            # Log failure reason if available
            failure_reason = data.get('gateway_response', 'Unknown reason')
            logger.warning(
                f"Payment failed: {reference} (event: {event_id}) - Amount: {payment.amount}, "
                f"User: {payment.user.id if payment.user else 'Anonymous'}, Reason: {failure_reason}",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
            
            # Add your business logic here
            # Examples:
            # - Send failure notification
            # - Log failure reason
            
        else:
            logger.info(
                f"Payment {reference} already has status {payment.status}, skipping update (event: {event_id})",
                extra={'user_id': payment.user.id if payment.user else 'Anonymous', 'tenant_id': 'N/A'}
            )
        
    except Payment.DoesNotExist:
        logger.warning(
            f"Payment not found for reference: {reference} (event: {event_id})",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )
    except Payment.MultipleObjectsReturned:
        logger.error(
            f"Multiple payments found with reference: {reference} (event: {event_id})",
            extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
        )


def handle_successful_transfer(data, event_id):
    """Handle successful transfer event (for payouts)"""
    # Implement if you're doing payouts
    logger.info(
        f"Transfer successful event {event_id} received (not implemented)",
        extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
    )


def handle_failed_transfer(data, event_id):
    """Handle failed transfer event (for payouts)"""
    # Implement if you're doing payouts
    logger.info(
        f"Transfer failed event {event_id} received (not implemented)",
        extra={'user_id': 'Webhook', 'tenant_id': 'N/A'}
    )