import logging
import time

logger = logging.getLogger('api')

class RequestLoggingMiddleware:
    """
    Middleware to log all incoming requests and their response status.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
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

