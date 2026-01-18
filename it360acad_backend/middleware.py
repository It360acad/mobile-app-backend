import logging
import time
import uuid

from it360acad_backend.logging_filters import request_contextvar

logger = logging.getLogger('api')


class RequestLoggingMiddleware:
    """
    Middleware to log all incoming requests and their response status.
    - Sets a request_id (correlation ID) on each request for log tracing.
    - Stores the request in a contextvar so TenantContextFilter can read client IP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        request_contextvar.set(request)
        try:
            # Store start time
            start_time = time.time()

            # Process the request
            response = self.get_response(request)

            # Calculate duration
            duration = time.time() - start_time

            # Get user info safely
            user_id = 'Anonymous'
            if hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id

            # Log the request details
            # Using the 'api' logger defined in Logger.py
            logger.info(
                f"{request.method} {request.get_full_path()} | Status: {response.status_code} | Duration: {duration:.2f}s",
                extra={
                    'tenant_id': getattr(request, 'tenant_id', 'N/A'),
                    'user_id': user_id
                }
            )

            return response
        finally:
            request_contextvar.set(None)

