
"""
Django LOGGING config. Best practices:
- detailed: human-readable, good for dev and small teams.
- json (LOG_FORMAT=json): one JSON object per line for production log aggregators
  (ELK, Loki, CloudWatch, Datadog). Enables querying by user_id, request_id, etc.
"""
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Try to get DEBUG from environment, default to False if not set
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# LOG_FORMAT=json for production / log aggregators (structured, one JSON per line)
LOG_FORMAT = os.environ.get('LOG_FORMAT', 'detailed')
_DEFAULT_FORMATTER = 'json' if LOG_FORMAT == 'json' else 'detailed'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'filters': {
        'tenant_context': {
            '()': 'it360acad_backend.logging_filters.TenantContextFilter',
        },
    },
    
    'formatters': {
        'detailed': {
            'format': '[{levelname}] {asctime} | request_id={request_id} | User: {user_display} | IP: {ip} | {name} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} | {message}',
            'style': '{',
        },
        'json': {
            '()': 'it360acad_backend.logging_filters.JsonFormatter',
        },
    },
    
    'handlers': {
        # Console - always on in development
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': _DEFAULT_FORMATTER,
            'filters': ['tenant_context'],
        },
        
        # App logs
        'app_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'app.log'),
            'maxBytes': 1024 * 1024 * 20,  # 20 MB
            'backupCount': 10,
            'formatter': _DEFAULT_FORMATTER,
            'filters': ['tenant_context'],
        },
        
        # Error logs (most important for pre-launch)
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'errors.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 15,
            'formatter': _DEFAULT_FORMATTER,
            'filters': ['tenant_context'],
        },
        
        # Security logs
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'security.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': _DEFAULT_FORMATTER,
            'filters': ['tenant_context'],
        },
        
        # API logs
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'api.log'),
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
            'formatter': _DEFAULT_FORMATTER,
            'filters': ['tenant_context'],
        },
    },
    
    'loggers': {
        'django': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'django.request': {
            'handlers': ['error_file', 'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        
        'authentication': {
            'handlers': ['security_file', 'console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'users': {
            'handlers': ['app_file', 'console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'courses': {
            'handlers': ['app_file', 'console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'api': {
            'handlers': ['api_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'notification': {
            'handlers': ['app_file', 'console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        'payments': {
            'handlers': ['security_file', 'app_file', 'console', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        
        '': {
            'handlers': ['console', 'app_file'],
            'level': 'INFO',
        },
    },
}

#  Email on critical errors 

ADMIN_EMAIL_SET = os.getenv('ADMIN_EMAIL')
if not DEBUG and ADMIN_EMAIL_SET:
    LOGGING['handlers']['mail_admins'] = {
        'level': 'CRITICAL',
        'class': 'django.utils.log.AdminEmailHandler',
        'formatter': _DEFAULT_FORMATTER,
        'filters': ['tenant_context'],
    }
    LOGGING['loggers']['django.request']['handlers'].append('mail_admins')
