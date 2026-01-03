

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Try to get DEBUG from environment, default to False if not set
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

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
            'format': '[{levelname}] {asctime} | Tenant: {tenant_id} | User: {user_id} | {name} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{levelname}] {asctime} | {message}',
            'style': '{',
        },
    },
    
    'handlers': {
        # Console - always on in development
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'filters': ['tenant_context'],
        },
        
        # App logs
        'app_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'app.log',
            'maxBytes': 1024 * 1024 * 20,  # 20 MB
            'backupCount': 10,
            'formatter': 'detailed',
            'filters': ['tenant_context'],
        },
        
        # Error logs (most important for pre-launch)
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 15,
            'formatter': 'detailed',
            'filters': ['tenant_context'],
        },
        
        # Security logs
        'security_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'detailed',
            'filters': ['tenant_context'],
        },
        
        # API logs
        'api_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api.log',
            'maxBytes': 1024 * 1024 * 15,  # 15 MB
            'backupCount': 10,
            'formatter': 'detailed',
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
        'formatter': 'detailed',
        'filters': ['tenant_context'],
    }
    LOGGING['loggers']['django.request']['handlers'].append('mail_admins')
