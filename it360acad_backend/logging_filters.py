import json
import logging
import contextvars
from datetime import datetime, timezone

# Holds the current request for the logging filter (set by middleware)
request_contextvar = contextvars.ContextVar('request', default=None)


class TenantContextFilter(logging.Filter):
    """
    """
    def filter(self, record):
        if not hasattr(record, 'tenant_id'):
            record.tenant_id = 'N/A'
        if not hasattr(record, 'user_id'):
            record.user_id = 'Anonymous'

        request = request_contextvar.get()

        # Resolve IP from current request when not already on the record
        if not hasattr(record, 'ip'):
            if request:
                xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
                record.ip = xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR', 'N/A')
            else:
                record.ip = 'N/A'

        # Request ID (correlation ID) for tracing all logs for one HTTP request
        if not hasattr(record, 'request_id'):
            record.request_id = getattr(request, 'request_id', 'N/A') if request else 'N/A'

        # When anonymous, use the client IP as the user identifier
        if record.user_id == 'Anonymous' and record.ip and record.ip != 'N/A':
            record.user_display = record.ip
        else:
            record.user_display = record.user_id

        return True


class JsonFormatter(logging.Formatter):
    """
    Emits one JSON object per log line. Use with LOG_FORMAT=json in production
    for log aggregators (ELK, Loki, CloudWatch, Datadog, etc.).
    """
    def format(self, record):
        log = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'user_id': getattr(record, 'user_id', 'N/A'),
            'user_display': getattr(record, 'user_display', 'N/A'),
            'ip': getattr(record, 'ip', 'N/A'),
            'request_id': getattr(record, 'request_id', 'N/A'),
        }
        if record.exc_info:
            log['exception'] = self.formatException(record.exc_info)
        return json.dumps(log)

