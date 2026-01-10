#!/bin/bash
# Helper script to set up Upstash Redis for Celery

echo "🔧 Setting up Upstash Redis for Celery..."
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ .env.local file not found!"
    exit 1
fi

# Get Redis URL from user
echo "Please enter your Upstash Redis URL:"
echo "Format: rediss://default:PASSWORD@apparent-labrador-33734.upstash.io:6379"
echo ""
read -p "Redis URL: " REDIS_URL

if [ -z "$REDIS_URL" ]; then
    echo "❌ Redis URL cannot be empty!"
    exit 1
fi

# Remove old CELERY_BROKER_URL if it exists
sed -i '/^CELERY_BROKER_URL=/d' .env.local
sed -i '/^CELERY_RESULT_BACKEND=/d' .env.local

# Add new configuration
echo "" >> .env.local
echo "# Celery Configuration - Upstash Redis" >> .env.local
echo "CELERY_BROKER_URL=\"$REDIS_URL\"" >> .env.local
echo "CELERY_RESULT_BACKEND=\"$REDIS_URL\"" >> .env.local

echo ""
echo "✅ Configuration updated!"
echo ""
echo "📋 Added to .env.local:"
echo "   CELERY_BROKER_URL=\"$REDIS_URL\""
echo "   CELERY_RESULT_BACKEND=\"$REDIS_URL\""
echo ""
echo "🧪 Now test the connection:"
echo "   python manage.py test_celery"
echo ""

