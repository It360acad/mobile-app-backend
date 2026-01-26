import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

from it360acad_backend.logging_filters import request_contextvar

logger = logging.getLogger('api')


class OptimizedRequestLoggingMiddleware(MiddlewareMixin):
    """
    Memory-optimized middleware for request logging in production environments.

    Optimizations:
    - Skip static file requests
    - Minimal request data logging
    - Efficient string formatting
    - Configurable log levels
    - Memory-conscious user info extraction
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

        # Skip logging for these paths to reduce memory usage
        self.skip_paths = {
            '/static/', '/media/', '/favicon.ico', '/robots.txt',
            '/health/', '/ping/', '/metrics/'
        }

        # Only log these methods in production (skip OPTIONS, HEAD)
        self.log_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE'}

    def should_log_request(self, request):
        """Determine if request should be logged to save memory"""
        # Skip static files
        if any(request.path.startswith(path) for path in self.skip_paths):
            return False

        # Skip certain methods
        if request.method not in self.log_methods:
            return False

        return True

    def get_user_info(self, request):
        """Memory-efficient user info extraction"""
        try:
            if hasattr(request, 'user') and request.user.is_authenticated:
                return str(request.user.id)
            return 'Anonymous'
        except Exception:
            return 'Unknown'

    def get_client_ip(self, request):
        """Get client IP efficiently"""
        # Check forwarded headers first (for reverse proxies)
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()

        return request.META.get('REMOTE_ADDR', 'Unknown')

    def process_request(self, request):
        """Set up request context"""
        if not self.should_log_request(request):
            return None

        # Generate minimal request ID
        request.request_id = str(uuid.uuid4())[:8]  # Shorter ID to save memory
        request._start_time = time.time()

        # Set context for other filters
        request_contextvar.set(request)

        return None

    def process_response(self, request, response):
        """Log request completion"""
        try:
            if not self.should_log_request(request):
                return response

            if not hasattr(request, '_start_time'):
                return response

            # Calculate duration
            duration = time.time() - request._start_time

            # Get user and IP info
            user_info = self.get_user_info(request)
            client_ip = self.get_client_ip(request)

            # Log level based on status code
            log_level = logging.INFO
            if response.status_code >= 400:
                log_level = logging.WARNING
            if response.status_code >= 500:
                log_level = logging.ERROR

            # Efficient log message formatting
            logger.log(
                log_level,
                f"{request.method} {request.path} | {response.status_code} | {duration:.2f}s",
                extra={
                    'request_id': getattr(request, 'request_id', 'N/A'),
                    'user_id': user_info,
                    'client_ip': client_ip,
                    'status_code': response.status_code,
                    'duration': round(duration, 2),
                    'method': request.method,
                    'path': request.path[:100],  # Limit path length
                }
            )

        except Exception as e:
            # Don't let logging errors break the response
            logger.error(f"Logging middleware error: {e}")
        finally:
            # Clean up context
            request_contextvar.set(None)

        return response

    def process_exception(self, request, exception):
        """Log exceptions"""
        try:
            if hasattr(request, '_start_time'):
                duration = time.time() - request._start_time
                user_info = self.get_user_info(request)

                logger.error(
                    f"EXCEPTION {request.method} {request.path} | {type(exception).__name__} | {duration:.2f}s",
                    extra={
                        'request_id': getattr(request, 'request_id', 'N/A'),
                        'user_id': user_info,
                        'exception_type': type(exception).__name__,
                        'exception_message': str(exception)[:200],  # Limit message length
                    },
                    exc_info=True
                )
        except Exception as e:
            # Don't let logging errors break exception handling
            pass
        finally:
            request_contextvar.set(None)

        return None


class MinimalRequestLoggingMiddleware(MiddlewareMixin):
    """
    Ultra-minimal request logging for maximum memory efficiency.
    Only logs errors and critical information.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

    def process_response(self, request, response):
        """Only log errors and slow requests"""
        try:
            # Only log problematic requests
            should_log = (
                response.status_code >= 400 or  # Errors
                getattr(request, '_duration', 0) > 5.0  # Slow requests
            )

            if should_log:
                duration = getattr(request, '_duration', 0)
                user_id = 'Auth' if (hasattr(request, 'user') and request.user.is_authenticated) else 'Anon'

                logger.warning(
                    f"{request.method} {request.path[:50]} | {response.status_code} | {duration:.1f}s | {user_id}"
                )
        except Exception:
            pass  # Ignore logging errors

        return response

    def process_request(self, request):
        """Track request start time"""
        request._start_time = time.time()
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Calculate duration after view processing"""
        if hasattr(request, '_start_time'):
            request._duration = time.time() - request._start_time
        return None


class NoRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that completely disables request logging.
    Use this in production if memory is extremely constrained.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        """Set minimal context without logging"""
        request.request_id = str(uuid.uuid4())[:8]
        request_contextvar.set(request)
        return None

    def process_response(self, request, response):
        """Clean up context without logging"""
        request_contextvar.set(None)
        return response

    def process_exception(self, request, exception):
        """Only log critical exceptions"""
        try:
            logger.critical(
                f"CRITICAL {request.method} {request.path} | {type(exception).__name__}",
                exc_info=True
            )
        except Exception:
            pass
        finally:
            request_contextvar.set(None)
        return None
