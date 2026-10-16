#!/usr/bin/env bash
# Ouvre la salle de réunion des agents dans le navigateur.
# Usage : scripts/salle-reunion.sh [port]   (8765 par défaut)
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8765}"
# Le Python de l'environnement des voix, s'il existe, pour profiter de Piper
PY=python3
if [ -x outils/salle-reunion/.venv/bin/python ]; then
  PY=outils/salle-reunion/.venv/bin/python
fi
( sleep 1.5 && xdg-open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true ) &
exec "$PY" outils/salle-reunion/serveur.py --port "$PORT"
