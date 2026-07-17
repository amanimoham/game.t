#!/usr/bin/env bash
set -euo pipefail

# Apply DB migrations, then launch the API.
echo "==> Running database migrations (alembic upgrade head)"
alembic upgrade head

echo "==> Starting API server"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers
