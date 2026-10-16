#!/bin/sh
# Attend PostgreSQL, applique les migrations, puis lance la commande demandee.
set -e

DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

echo "[entrypoint] Attente de PostgreSQL sur ${DB_HOST}:${DB_PORT}..."
until python -c "import socket,sys; s=socket.socket(); s.settimeout(2); sys.exit(0 if s.connect_ex(('${DB_HOST}', ${DB_PORT})) == 0 else 1)"; do
  sleep 1
done
echo "[entrypoint] PostgreSQL est pret."

echo "[entrypoint] Application des migrations..."
python manage.py migrate --noinput

exec "$@"
