import os
from signal import default_int_handler
from dotenv import load_dotenv
from pathlib import Path
import dj_database_url
import warnings
import sys
from contextlib import redirect_stderr
from io import StringIO

# Suppress python-dotenv warnings for parsing errors
warnings.filterwarnings('ignore', category=UserWarning, module='dotenv')

# Load .env files with error handling (suppress stderr output from parsing errors)
try:
    with redirect_stderr(StringIO()):
        load_dotenv(verbose=False)  # Load .env
except Exception:
    pass

try:
    with redirect_stderr(StringIO()):
        load_dotenv('.env.local', verbose=False)  # Load .env.local (takes precedence)
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# For Render deployment
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, 'localhost', '127.0.0.1']
    additional_hosts = os.getenv('ALLOWED_HOSTS', '').split(',')
    ALLOWED_HOSTS.extend([h.strip() for h in additional_hosts if h.strip()])
else:
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

AUTH_USER_MODEL = 'users.User'

if not DEBUG:
    # HTTPS Security Settings (Required for production)
    SECURE_SSL_REDIRECT = True  # Redirect all HTTP to HTTPS
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust proxy headers (Render, etc.)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'    #  Prevent clickjacking attacks
    SECURE_HSTS_SECONDS = 31536000  #  HSTS for 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  #  HSTS for all subdomains
    SECURE_HSTS_PRELOAD = True  #  HSTS for preload
    SESSION_COOKIE_SECURE = True  # Only send session cookies over HTTPS
    CSRF_COOKIE_SECURE = True  # Only send CSRF cookies over HTTPS


#  Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'authentication',
    'users',
    'courses',
    'rest_framework',
    'drf_spectacular',
    'anymail',
    'notification',
    'channels',
    'chat',
    'payments',
]


# Channels configuration
ASGI_APPLICATION = 'it360acad_backend.asgi.application'

# Upstash Redis configuration for Channels
REDIS_URL = os.getenv('REDIS_URL') or os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# Channel layers configuration (uses database 2 for channels, separate from Celery and cache)
if REDIS_URL and (REDIS_URL.startswith('rediss://') or REDIS_URL.startswith('redis://')):
    # Parse Redis URL for channels (use database 2)
    import re
    from urllib.parse import urlparse
    
    # Parse the Redis URL
    parsed = urlparse(REDIS_URL.replace('rediss://', 'redis://'))
    
    # Extract components
    host = parsed.hostname
    port = parsed.port or 6379
    password = parsed.password
    db = 2  # Use database 2 for channels
    
    # Build connection config
    if REDIS_URL.startswith('rediss://'):
        # For TLS connections
        import ssl
        connection_config = {
            'address': (host, port),
            'ssl': True,
            'ssl_cert_reqs': ssl.CERT_NONE,
        }
        if password:
            connection_config['password'] = password
    else:
        # For non-TLS connections
        connection_config = {
            'address': (host, port),
        }
        if password:
            connection_config['password'] = password
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [connection_config],
            },
        },
    }
else:
    # Fallback to in-memory channel layer for development
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# drf-spectacular settings
SPECTACULAR_SETTINGS = {
    'TITLE': 'IT360 Academy API',
    'DESCRIPTION': 'API documentation for IT360 Academy',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'ENUM_NAME_OVERRIDES': {
        'UserRoleEnum': [
            ('student', 'Student'),
            ('parent', 'Parent'),
            ('admin', 'Admin'),
        ],
    },
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

#  Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'it360acad_backend.middleware.RequestLoggingMiddleware',  # Added Request Logging
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'it360acad_backend.urls'

#  Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#  WSGI application
WSGI_APPLICATION = 'it360acad_backend.wsgi.application'

#  Database

if os.environ.get('DB_URL'):
    # Production: Use Supabase
    db_config = dj_database_url.config(
        default=os.environ.get('DB_URL'),
        conn_max_age=600,
        conn_health_checks=False,  # Disable health checks to prevent timeouts
        ssl_require=True
    )
    
    # Ensure database name is set (Supabase default is 'postgres' if not specified)
    if not db_config.get('NAME'):
        db_url = os.environ.get('DB_URL', '')
        import re
        # Pattern: postgresql://user:pass@host:port/dbname
        match = re.search(r'/([^/?]+)(?:\?|$)', db_url.split('@')[-1] if '@' in db_url else db_url)
        if match:
            db_config['NAME'] = match.group(1)
        else:
            # Default to 'postgres' for Supabase if not found
            db_config['NAME'] = 'postgres'
    
    # Add connection timeout options to prevent hanging
    db_config.setdefault('OPTIONS', {})
    # Merge existing OPTIONS if any
    existing_options = db_config.get('OPTIONS', {})
    db_config['OPTIONS'] = {
        **existing_options,
        'connect_timeout': 10,  # 10 second connection timeout
    }
    
    DATABASES = {
        'default': db_config
    }
else:
    #  Development uses local PostgreSQL
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'it360_app',
        'USER': 'it360_admin',
        'PASSWORD': 'it360123',
        'HOST': 'localhost',
        'PORT': '5432',
        }
    }


    # Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


#  Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise configuration for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (if needed)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173').split(',')

# For development, you can also use:
# CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only allow all origins in DEBUG mode

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

#  Anymail configuration (Resend API)
ANYMAIL = {
    "RESEND_API_KEY": os.getenv("RESEND_API_KEY"),
}

# Resend Email Configuration
USE_CONSOLE_EMAIL = os.getenv('USE_CONSOLE_EMAIL', 'False').lower() == 'true'

if USE_CONSOLE_EMAIL:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: Use Resend API via Anymail (Much more reliable than SMTP on Render)
    EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"

# Default email settings
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'onboarding@resend.dev')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Admins for error reporting
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
if ADMIN_EMAIL:
    ADMINS = [('Admin', ADMIN_EMAIL)]


redis_url = os.getenv('REDIS_URL')
celery_broker = os.getenv('CELERY_BROKER_URL', '')
if celery_broker and not celery_broker.startswith(('redis://', 'rediss://')):
    celery_broker = None
CELERY_BROKER_URL = redis_url or celery_broker or 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND') or CELERY_BROKER_URL

# SSL Configuration for Upstash Redis (required when using rediss:// with TLS)
if CELERY_BROKER_URL.startswith('rediss://'):
    import ssl
    CELERY_BROKER_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE,  # Upstash uses self-signed certificates
    }
    CELERY_REDIS_BACKEND_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE,
    }

# Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Task execution settings
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Task routing (optional - for future use with multiple queues)
CELERY_TASK_ROUTES = {
    'notification.tasks.*': {'queue': 'notifications'},
    # Add more routes as needed for other apps
}

# Django Cache Configuration (using Redis/Upstash)
# Use the same Redis connection as Celery, but with a different database number
redis_url = os.getenv('REDIS_URL') or os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
# Use database 1 for cache (Celery uses database 0)
if redis_url.startswith('rediss://'):
    # For TLS connections, replace /0 with /1
    cache_url = redis_url.rsplit('/', 1)[0] + '/1'
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': cache_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'SSL_CERT_REQS': ssl.CERT_NONE,  # Upstash uses self-signed certificates
            },
            'KEY_PREFIX': 'it360acad',
            'TIMEOUT': 3600,  # Default timeout: 1 hour
        }
    }
elif redis_url.startswith('redis://'):
    cache_url = redis_url.rsplit('/', 1)[0] + '/1'
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': cache_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'it360acad',
            'TIMEOUT': 3600,  # Default timeout: 1 hour
        }
    }
else:
    # Fallback to local memory cache if Redis not configured
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Logging Configuration
from .logger.Logger import LOGGING


# PAYMENT SETTINGS
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

# Validate secret keys in production
if not DEBUG:
    # Validate Django SECRET_KEY
    if SECRET_KEY == 'django-insecure-dev-key-change-in-production':
        raise ValueError(
            "SECRET_KEY must be set in production! "
            "Set SECRET_KEY environment variable with a secure random value."
        )
    
    # Validate Paystack keys
    if not PAYSTACK_SECRET_KEY:
        raise ValueError(
            "PAYSTACK_SECRET_KEY must be set in production! "
            "Set PAYSTACK_SECRET_KEY environment variable."
        )
    
    if not PAYSTACK_PUBLIC_KEY:
        raise ValueError(
            "PAYSTACK_PUBLIC_KEY must be set in production! "
            "Set PAYSTACK_PUBLIC_KEY environment variable."
        )
    
    # Warn if keys look insecure (too short or contain common patterns)
    if len(SECRET_KEY) < 50:
        import warnings
        warnings.warn(
            "SECRET_KEY appears to be too short. Use a longer, randomly generated key.",
            UserWarning
        )
    
    if PAYSTACK_SECRET_KEY and len(PAYSTACK_SECRET_KEY) < 20:
        import warnings
        warnings.warn(
            "PAYSTACK_SECRET_KEY appears to be too short. Verify your Paystack secret key.",
            UserWarning
        )
else:
    # Development warnings (suppressed for expected missing keys)
    if SECRET_KEY == 'django-insecure-dev-key-change-in-production':
        # Only warn in development if explicitly needed
        pass  # Suppressed: expected in development
    
    # Suppress PAYSTACK key warnings in development - they're expected to be missing
    # Payment features will fail gracefully if keys are not set