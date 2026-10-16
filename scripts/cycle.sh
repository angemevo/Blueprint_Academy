#!/usr/bin/env bash
# Lance un cycle de l'équipe d'agents en mode headless, avec l'abonnement Claude Pro.
# Usage : scripts/cycle.sh pilotage|tech
# Variable optionnelle : NTFY_TOPIC=mon-sujet-secret (notification sur téléphone via ntfy.sh)

set -uo pipefail

CYCLE="${1:-}"
case "$CYCLE" in
  pilotage|tech) ;;
  *) echo "Usage : $0 pilotage|tech" >&2; exit 2 ;;
esac

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR" || exit 1

# cron démarre avec un PATH minimal : on ajoute les emplacements usuels de node, gh et claude
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/.nvm/nvm.sh" >/dev/null
fi

mkdir -p logs
STAMP="$(date +%F_%H%M)"
# Un événement JSON par ligne : la salle de réunion (outils/salle-reunion) le lit en direct
LOG="logs/${STAMP}-${CYCLE}.jsonl"

notifier() {
  if [ -n "${NTFY_TOPIC:-}" ]; then
    curl -s -m 10 -H "Title: Agents - cycle $CYCLE" -d "$1" "https://ntfy.sh/$NTFY_TOPIC" >/dev/null || true
  fi
}

# Un seul cycle à la fois
exec 9>"/tmp/agents-$(basename "$REPO_DIR").lock"
if ! flock -n 9; then
  echo "Un cycle tourne déjà, abandon." >&2
  exit 0
fi

for outil in claude gh git docker; do
  if ! command -v "$outil" >/dev/null 2>&1; then
    notifier "Échec : $outil introuvable dans le PATH de cron."
    echo "$outil introuvable" >&2
    exit 1
  fi
done

# Point de départ propre : branche principale à jour, aucune modification de code en attente
if [ -n "$(git status --porcelain -- . ':!state' ':!reports' ':!logs' ':!frontend/next-env.d.ts')" ]; then
  notifier "Cycle annulé : modifications non commitées dans le dépôt."
  echo "Modifications non commitées hors state/ et reports/, cycle annulé." >&2
  exit 1
fi
BRANCHE="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
BRANCHE="${BRANCHE:-master}"
git switch -q "$BRANCHE" && git pull -q --ff-only || {
  notifier "Cycle annulé : impossible de mettre $BRANCHE à jour."
  exit 1
}

# La stack Docker doit tourner pour que les agents lancent tests et vérifications
if [ ! -f .env ]; then
  notifier "Cycle annulé : fichier .env absent (cp .env.example .env)."
  echo ".env absent" >&2
  exit 1
fi
if ! docker compose up -d --wait postgres backend frontend >/dev/null 2>&1; then
  notifier "Cycle annulé : la stack Docker ne démarre pas (docker compose up)."
  exit 1
fi

# En mode -p, Claude Code ignore les autorisations de .claude/settings.json tant que le dossier
# n'a pas été approuvé une fois en session interactive : sans elles, les agents ne peuvent ni
# lancer gh ni les tests. On s'arrête tout de suite plutôt que de consommer du quota pour rien.
CONFIG_CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json"
if ! python3 - "$CONFIG_CLAUDE" "$(git rev-parse --show-toplevel)" <<'PY'
import json, sys
try:
    projets = json.load(open(sys.argv[1])).get("projects", {})
except (OSError, ValueError):
    sys.exit(1)
sys.exit(0 if projets.get(sys.argv[2], {}).get("hasTrustDialogAccepted") else 1)
PY
then
  printf '{"type":"cycle_start","cycle":"%s","started_at":"%s"}\n{"type":"system","subtype":"dossier_non_approuve","message":"Lance claude une fois dans le dépôt et accepte l approbation du dossier."}\n{"type":"cycle_end","cycle":"%s","exit_code":3,"ended_at":"%s"}\n' \
    "$CYCLE" "$(date -Iseconds)" "$CYCLE" "$(date -Iseconds)" > "$LOG"
  notifier "Cycle annulé : dossier non approuvé. Lance « claude » une fois dans $REPO_DIR et accepte."
  echo "Dossier non approuvé par Claude Code : lance « claude » une fois dans $REPO_DIR et accepte." >&2
  exit 3
fi

# Le texte des sous-agents n'est transmis qu'avec une version récente de Claude Code
OPTIONS_FLUX=(--output-format stream-json --verbose)
if claude --help 2>/dev/null | grep -q -- "--forward-subagent-text"; then
  OPTIONS_FLUX+=(--forward-subagent-text)
fi

# Marqueur de début, utile à la salle de réunion
printf '{"type":"cycle_start","cycle":"%s","started_at":"%s"}\n' "$CYCLE" "$(date -Iseconds)" > "$LOG"

# Le cycle lui-même. timeout = garde-fou si une session ne s'arrête pas.
timeout 90m claude -p "/cycle-$CYCLE" \
  --permission-mode acceptEdits \
  --permission-prompts none \
  "${OPTIONS_FLUX[@]}" >> "$LOG" 2>> "logs/${STAMP}-${CYCLE}.err"
STATUT=$?
printf '{"type":"cycle_end","cycle":"%s","exit_code":%d,"ended_at":"%s"}\n' "$CYCLE" "$STATUT" "$(date -Iseconds)" >> "$LOG"

# Les agents peuvent finir sur une branche de travail : on revient sur la branche principale
if [ "$(git branch --show-current)" != "$BRANCHE" ]; then
  if ! git switch -q "$BRANCHE"; then
    notifier "Cycle terminé mais retour sur $BRANCHE impossible : à vérifier à la main."
    exit 1
  fi
fi

if [ "$STATUT" -ne 0 ]; then
  echo "| $(date +%F) | cycle-$CYCLE | - | coupé (code $STATUT) |" >> state/quota.md
fi

# L'état de l'équipe est committé sur la branche principale par ce script, jamais par les agents
if [ -n "$(git status --porcelain -- state reports)" ]; then
  git add state reports
  git commit -q -m "État des agents : cycle $CYCLE du $(date +%F)"
  git push -q origin "$BRANCHE" || notifier "Push de l'état sur $BRANCHE refusé : vérifie la protection de branche."
fi

if [ "$STATUT" -eq 0 ]; then
  RESUME="$(command -v jq >/dev/null && grep '"type":"result"' "$LOG" | tail -1 | jq -r '.result // empty' 2>/dev/null | head -c 600)"
  notifier "${RESUME:-Cycle terminé.}"
else
  notifier "Cycle arrêté (code $STATUT) : quota atteint ou erreur. Voir $LOG"
fi

exit "$STATUT"
