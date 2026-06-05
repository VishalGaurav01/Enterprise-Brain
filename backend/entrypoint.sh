#!/bin/sh
set -e

echo "⏳ Waiting for database to be ready..."
until python -c "
import socket, os, sys
host = os.environ.get('POSTGRES_HOST', 'db')
port = int(os.environ.get('POSTGRES_PORT', 5432))
try:
    s = socket.create_connection((host, port), timeout=3)
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "   Database not ready yet — retrying in 2s..."
  sleep 2
done

echo "✅ Database is ready."
echo "🔄 Running Alembic migrations..."
alembic upgrade head
echo "✅ Migrations complete."

echo "🚀 Starting application: $@"
exec "$@"
