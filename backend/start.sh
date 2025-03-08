#!/bin/bash
set -e

# Start Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &
export DISPLAY=:99

# Wait for Xvfb to start
sleep 1

echo "Starting application..."
# Start the application with increased timeout and gevent worker
exec gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers=2 \
    --threads=4 \
    --worker-class=gthread \
    --timeout=120 \
    --log-level=info 