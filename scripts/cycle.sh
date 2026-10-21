#!/usr/bin/env bash
# Point d'entrée du travail de l'équipe d'agents (GitHub Actions ou cron d'un ordinateur).
# Usage : scripts/cycle.sh nuit|tech|courrier|matin|pilotage|rapport
# Le travail lui-même est décrit et fait par scripts/equipe.py.
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

# cron démarre avec un PATH minimal : on AJOUTE les emplacements usuels de node, gh et claude.
# (Ajouter à la fin, pas au début : sur GitHub, le Python installé par setup-python, celui qui a
# reportlab et playwright, doit rester devant le Python du système.)
export PATH="$PATH:$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/.nvm/nvm.sh" >/dev/null
fi
mkdir -p logs
exec python3 scripts/equipe.py "$@"
