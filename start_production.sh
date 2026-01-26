#!/bin/bash

# Production startup script for IT360 Academy Backend
# This script starts both the Django server and Celery worker for production

set -e  # Exit on any error

echo "🚀 Starting IT360 Academy Backend in Production Mode..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Activating .venv..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        print_status "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please create one with: python -m venv .venv"
        exit 1
    fi
fi

# Check environment variables
print_info "Checking environment variables..."

# Required environment variables
REQUIRED_VARS=(
    "SECRET_KEY"
    "DB_URL"
    "CELERY_BROKER_URL"
)

MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    print_error "Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    print_info "Please set these in your .env file or environment"
    exit 1
fi

print_status "Environment variables check passed"

# Check if Redis/Upstash is accessible
print_info "Testing Redis connection..."
if python -c "
import os
import redis
from urllib.parse import urlparse

redis_url = os.environ.get('CELERY_BROKER_URL')
if not redis_url:
    print('❌ CELERY_BROKER_URL not set')
    exit(1)

try:
    # Parse URL to handle both redis:// and rediss://
    parsed = urlparse(redis_url)
    if parsed.scheme == 'rediss':
        # TLS connection
        r = redis.from_url(redis_url, ssl_cert_reqs=None)
    else:
        r = redis.from_url(redis_url)

    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    exit(1)
"; then
    print_status "Redis connection test passed"
else
    print_error "Redis connection failed. Please check your CELERY_BROKER_URL"
    exit 1
fi

# Run database migrations
print_info "Running database migrations..."
if python manage.py migrate --check > /dev/null 2>&1; then
    print_status "Database is up to date"
else
    print_info "Running migrations..."
    python manage.py migrate
    print_status "Database migrations completed"
fi

# Collect static files if needed
if [ "$COLLECT_STATIC" = "true" ]; then
    print_info "Collecting static files..."
    python manage.py collectstatic --noinput
    print_status "Static files collected"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop any existing processes
print_info "Stopping existing processes..."
if [ -f "celery_worker.pid" ]; then
    ./stop_celery_worker.sh || true
fi

# Kill any existing gunicorn processes
pkill -f "gunicorn.*it360acad_backend" || true

# Start Celery worker in background
print_info "Starting Celery worker..."
./start_celery_worker.sh
print_status "Celery worker started"

# Start the Django server
print_info "Starting Django server..."

# Use Gunicorn for production
if command -v gunicorn &> /dev/null; then
    print_info "Using Gunicorn for production server..."

    # Default configuration
    WORKERS=${GUNICORN_WORKERS:-4}
    BIND=${BIND:-"0.0.0.0:8000"}
    TIMEOUT=${GUNICORN_TIMEOUT:-120}

    print_info "Server configuration:"
    print_info "  - Workers: $WORKERS"
    print_info "  - Bind: $BIND"
    print_info "  - Timeout: $TIMEOUT seconds"

    # Start Gunicorn
    exec gunicorn it360acad_backend.wsgi:application \
        --workers $WORKERS \
        --bind $BIND \
        --timeout $TIMEOUT \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        --log-level info \
        --preload \
        --max-requests 1000 \
        --max-requests-jitter 100
else
    print_warning "Gunicorn not found. Using Django development server (not recommended for production)"
    exec python manage.py runserver 0.0.0.0:8000
fi
