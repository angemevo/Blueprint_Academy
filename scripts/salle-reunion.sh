#!/usr/bin/env bash
# Ouvre la salle de réunion des agents dans le navigateur.
# Usage : scripts/salle-reunion.sh [port]   (8765 par défaut)
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${1:-8765}"
( sleep 1.5 && xdg-open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true ) &
exec python3 outils/salle-reunion/serveur.py --port "$PORT"
