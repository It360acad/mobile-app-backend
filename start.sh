#!/usr/bin/env bash
# Startup script for Render deployment
# Ensures gunicorn binds to 0.0.0.0 for Render port detection
# This script MUST be used as the Start Command in Render dashboard

set -o errexit

# Get PORT from environment (Render sets this automatically)
PORT="${PORT:-8000}"

# Start gunicorn with explicit 0.0.0.0 binding
# The --bind parameter MUST come last to override any Render-added bind settings
exec gunicorn it360acad_backend.wsgi:application \
    --config gunicorn_config.py \
    --bind "0.0.0.0:${PORT}"

