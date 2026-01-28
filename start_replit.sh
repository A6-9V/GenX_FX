#!/bin/bash

# Exit on error
set -e

echo "Starting GenX-FX on Replit..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

# Run database migrations if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL is not set. Skipping database migrations."
  echo "Note: Node.js backend requires Postgres for full functionality."
else
  echo "Running database migrations..."
  npm run db:migrate
fi

# Build frontend
echo "Building frontend..."
npm run build

# Start Python backend in background
echo "Starting Python backend..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &
PID_PYTHON=$!

# Wait a bit for Python backend to start
sleep 5

# Start Node backend
echo "Starting Node backend..."
# Use PORT env var if available, otherwise default to 5000 (but Replit sets PORT usually)
export NODE_ENV=production
# Replit might set PORT to 8080 or something else. We should use it for the main server.
# The Node server uses process.env.PORT || 5000.
npm start

# Cleanup on exit
trap "kill $PID_PYTHON" EXIT
