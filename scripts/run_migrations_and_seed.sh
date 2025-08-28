#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../" || exit 1

echo "Running database migrations and seed..."

if command -v alembic >/dev/null 2>&1; then
  echo "Running alembic upgrade head (local)"
  alembic upgrade head
else
  echo "alembic CLI not found. Attempting to run via python -m alembic"
  python -m alembic upgrade head
fi

echo "Seeding super admin..."
python scripts/seed_super_admin.py

echo "Migrations and seed complete."
