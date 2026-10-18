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
# Les cycles qui ont tourné sur GitHub sont publiés sur la branche « livrables » :
# on récupère leurs journaux pour pouvoir les rejouer ici.
mkdir -p logs
if git fetch -q origin livrables 2>/dev/null; then
  git archive origin/livrables journaux 2>/dev/null | tar -x -C logs --strip-components=1 --skip-old-files 2>/dev/null || true
fi
( sleep 1.5 && xdg-open "http://127.0.0.1:$PORT" >/dev/null 2>&1 || true ) &
exec "$PY" outils/salle-reunion/serveur.py --port "$PORT"
