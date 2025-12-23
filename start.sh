#!/usr/bin/env bash
# Startup script for Render deployment
# Ensures gunicorn binds to 0.0.0.0 for Render port detection

set -o errexit

# Get PORT from environment (Render sets this automatically)
PORT="${PORT:-8000}"

# Start gunicorn with explicit 0.0.0.0 binding
exec gunicorn it360acad_backend.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --config gunicorn_config.py

