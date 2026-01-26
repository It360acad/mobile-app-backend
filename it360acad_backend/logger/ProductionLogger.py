"""
Production-optimized Django LOGGING configuration for memory-constrained environments.
Designed for Render, Heroku, and other cloud platforms with limited memory.

Key optimizations:
- Reduced memory footprint
- Faster log rotation
- Console-first with minimal file logging
- JSON format for log aggregators
- Efficient buffering
"""
import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Ensure logs directory exists (but use it sparingly)
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Environment detection
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
IS_PRODUCTION = not DEBUG

# Production logging strategy
DISABLE_FILE_LOGGING = os.environ.get('DISABLE_FILE_LOGGING', 'False') == 'True'
USE_JSON_LOGS = os.environ.get('LOG_FORMAT', 'json') == 'json'

# Memory-efficient settings
PRODUCTION_LOG_SETTINGS = {
    'max_file_size': 1024 * 1024 * 5,  # 5MB (reduced from 20MB)
    'backup_count': 3,  # Keep only 3 backups (reduced from 10+)
    'buffer_size': 1024,  # Small buffer to reduce memory usage
    'flush_level': 'ERROR',  # Only force flush on errors
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'filters': {
        'tenant_context': {
            '()': 'it360acad_backend.logging_filters.TenantContextFilter',
        },
        'skip_static': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not (
                hasattr(record, 'request') and
                record.request.path.startswith(('/static/', '/media/', '/favicon.ico'))
            ),
        },
    },

    'formatters': {
        'production': {
            '()': 'it360acad_backend.logging_filters.JsonFormatter',
        } if USE_JSON_LOGS else {
            'format': '[{levelname}] {asctime} | {name} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'console': {
            'format': '[{levelname}] {name} | {message}',
            'style': '{',
        },
        'error': {
            'format': '[{levelname}] {asctime} | {name} | {pathname}:{lineno} | {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },

    'handlers': {
        # Primary handler - console output (Render/cloud-friendly)
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'production' if IS_PRODUCTION else 'console',
            'filters': ['skip_static'] if IS_PRODUCTION else [],
        },

        # Critical errors only - small file
        'critical_file': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'critical.log'),
            'maxBytes': PRODUCTION_LOG_SETTINGS['max_file_size'] // 2,  # 2.5MB
            'backupCount': 2,
            'formatter': 'error',
            'filters': ['tenant_context'],
        } if not DISABLE_FILE_LOGGING else {
            'level': 'CRITICAL',
            'class': 'logging.NullHandler',
        },

        # Null handler for disabled logging
        'null': {
            'class': 'logging.NullHandler',
        },
    },
}

# Add conditional handlers based on environment
if not DISABLE_FILE_LOGGING and not IS_PRODUCTION:
    # Development: Add minimal file logging
    LOGGING['handlers'].update({
        'dev_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOGS_DIR / 'dev_errors.log'),
            'maxBytes': PRODUCTION_LOG_SETTINGS['max_file_size'],
            'backupCount': PRODUCTION_LOG_SETTINGS['backup_count'],
            'formatter': 'error',
            'filters': ['tenant_context'],
        },
    })

# Logger configuration - optimized for production
LOGGING['loggers'] = {
    # Root logger - console only in production
    '': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },

    # Django framework
    'django': {
        'handlers': ['console'],
        'level': 'WARNING' if IS_PRODUCTION else 'INFO',
        'propagate': False,
    },

    # Critical Django errors
    'django.request': {
        'handlers': ['console', 'critical_file'],
        'level': 'ERROR',
        'propagate': False,
    },

    'django.security': {
        'handlers': ['console', 'critical_file'],
        'level': 'WARNING',
        'propagate': False,
    },

    # Application loggers - console first
    'authentication': {
        'handlers': ['console'] + (['dev_file'] if 'dev_file' in LOGGING['handlers'] else []),
        'level': 'INFO',
        'propagate': False,
    },

    'users': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },

    'courses': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },

    'notification': {
        'handlers': ['console'],
        'level': 'INFO',
        'propagate': False,
    },

    'payments': {
        'handlers': ['console', 'critical_file'],  # Financial ops need critical logging
        'level': 'INFO',
        'propagate': False,
    },

    # API requests - reduced logging in production
    'api': {
        'handlers': ['console'],
        'level': 'WARNING' if IS_PRODUCTION else 'INFO',
        'propagate': False,
    },

    # Celery - minimal logging
    'celery': {
        'handlers': ['console'],
        'level': 'WARNING',
        'propagate': False,
    },

    # Third-party loggers - silence or minimize
    'urllib3': {
        'handlers': ['null'] if IS_PRODUCTION else ['console'],
        'level': 'WARNING',
        'propagate': False,
    },

    'requests': {
        'handlers': ['null'] if IS_PRODUCTION else ['console'],
        'level': 'WARNING',
        'propagate': False,
    },

    'django.db.backends': {
        'handlers': ['null'] if IS_PRODUCTION else ['console'],
        'level': 'WARNING',
        'propagate': False,
    },
}

# Production-specific optimizations
if IS_PRODUCTION:
    # Disable debug logging completely
    for logger_name, logger_config in LOGGING['loggers'].items():
        if logger_config['level'] == 'DEBUG':
            logger_config['level'] = 'INFO'

    # Add memory-efficient email handler for critical errors
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    if ADMIN_EMAIL:
        LOGGING['handlers']['mail_admins'] = {
            'level': 'CRITICAL',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'error',
            'include_html': False,  # Reduce memory usage
        }
        LOGGING['loggers']['django.request']['handlers'].append('mail_admins')

# Environment-specific settings
PRODUCTION_LOGGING_TIPS = {
    'render': {
        'LOG_FORMAT': 'json',
        'DISABLE_FILE_LOGGING': 'True',
        'DJANGO_LOG_LEVEL': 'WARNING',
    },
    'heroku': {
        'LOG_FORMAT': 'json',
        'DISABLE_FILE_LOGGING': 'True',
        'DJANGO_LOG_LEVEL': 'WARNING',
    },
    'development': {
        'LOG_FORMAT': 'detailed',
        'DISABLE_FILE_LOGGING': 'False',
        'DJANGO_LOG_LEVEL': 'INFO',
    }
}

# Ultra-minimal logging configuration (only errors and critical)
ULTRA_MINIMAL_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'minimal': {
            'format': '[{levelname}] {name} | {message}',
            'style': '{',
        },
    },

    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'minimal',
        },
    },

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'authentication': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'payments': {
            'handlers': ['console'],
            'level': 'WARNING',  # Keep payment warnings
            'propagate': False,
        },
    },
}

# Choose logging configuration based on ULTRA_MINIMAL setting
if os.environ.get('ULTRA_MINIMAL_LOGGING', 'False') == 'True':
    LOGGING = ULTRA_MINIMAL_LOGGING

# Memory usage summary
ESTIMATED_MEMORY_USAGE = {
    'ultra_minimal': '< 5MB (errors only)',
    'console_only': '< 10MB',
    'with_critical_files': '< 20MB',
    'with_full_files': '50-100MB',
    'recommendation': 'Use ultra_minimal for extreme memory constraints'
}
