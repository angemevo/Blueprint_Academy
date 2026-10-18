#!/usr/bin/env bash
# Lance un cycle de l'équipe d'agents en mode headless, avec l'abonnement Claude Pro.
# Usage : scripts/cycle.sh pilotage|tech|rapport
#   pilotage : bilan de la semaine, plan de la suivante, puis rapport PDF (dimanche)
#   tech     : une issue développée, relue, puis mergée par le portier si tout est vert
#   rapport  : régénère seulement le PDF de la semaine, sans Claude
# Tourne sur GitHub Actions (.github/workflows/agents.yml) ou sur un ordinateur (cron).
# Variables optionnelles : NTFY_TOPIC (notification téléphone), QUOTA_MAX_SEMAINE (0.70 par défaut).

set -uo pipefail

CYCLE="${1:-}"
case "$CYCLE" in
  pilotage|tech|rapport) ;;
  *) echo "Usage : $0 pilotage|tech|rapport" >&2; exit 2 ;;
esac

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR" || exit 1
EN_CLOUD="${GITHUB_ACTIONS:-}"

# cron démarre avec un PATH minimal : on ajoute les emplacements usuels de node, gh et claude
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  # shellcheck disable=SC1091
  . "$HOME/.nvm/nvm.sh" >/dev/null
fi

mkdir -p logs
STAMP="$(date +%F_%H%M)"
SEMAINE="$(date +%G-S%V)"
# Un événement JSON par ligne : la salle de réunion (outils/salle-reunion) le lit en direct
LOG="logs/${STAMP}-${CYCLE}.jsonl"
QUOTA_MAX_SEMAINE="${QUOTA_MAX_SEMAINE:-0.70}"

notifier() {
  if [ -n "${NTFY_TOPIC:-}" ]; then
    curl -s -m 10 -H "Title: Agents - cycle $CYCLE" -d "$1" "https://ntfy.sh/$NTFY_TOPIC" >/dev/null || true
  fi
  echo "[notification] $1"
}

# Un seul cycle à la fois
exec 9>"/tmp/agents-$(basename "$REPO_DIR").lock"
if ! flock -n 9; then
  echo "Un cycle tourne déjà, abandon." >&2
  exit 0
fi

OUTILS="gh git python3"
[ "$CYCLE" != "rapport" ] && OUTILS="$OUTILS claude"
[ "$CYCLE" = "tech" ] && OUTILS="$OUTILS docker"
for outil in $OUTILS; do
  if ! command -v "$outil" >/dev/null 2>&1; then
    notifier "Échec : $outil introuvable."
    exit 1
  fi
done

# Point de départ propre : branche principale à jour, aucune modification de code en attente
if [ -n "$(git status --porcelain -- . ':!state' ':!reports' ':!logs' ':!frontend/next-env.d.ts')" ]; then
  notifier "Cycle annulé : modifications non commitées dans le dépôt."
  exit 1
fi
BRANCHE="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
BRANCHE="${BRANCHE:-master}"
git switch -q "$BRANCHE" && git pull -q --ff-only || {
  notifier "Cycle annulé : impossible de mettre $BRANCHE à jour."
  exit 1
}

# Garde-fou quota : au-delà de QUOTA_MAX_SEMAINE du quota hebdomadaire, plus de cycle tech
# (le reste de l'abonnement est pour Ange). state/quota.json est mis à jour à chaque cycle.
if [ "$CYCLE" = "tech" ] && ! python3 - "$QUOTA_MAX_SEMAINE" <<'PY'
import json, sys, time
try:
    q = json.load(open("state/quota.json"))["seven_day"]
except (OSError, ValueError, KeyError):
    sys.exit(0)
plein = q.get("utilization", 0) >= float(sys.argv[1]) and q.get("resetsAt", 0) > time.time()
sys.exit(1 if plein else 0)
PY
then
  notifier "Cycle tech sauté : l'équipe a utilisé sa part du quota Claude de la semaine (${QUOTA_MAX_SEMAINE})."
  exit 0
fi

if [ "$CYCLE" = "tech" ]; then
  # La stack Docker doit tourner pour que les agents lancent tests et vérifications
  [ -f .env ] || { [ -n "$EN_CLOUD" ] && cp .env.example .env; }
  if [ ! -f .env ]; then
    notifier "Cycle annulé : fichier .env absent (cp .env.example .env)."
    exit 1
  fi
  if ! docker compose up -d --build --wait postgres backend frontend >"logs/${STAMP}-docker.log" 2>&1; then
    notifier "Cycle annulé : la stack Docker ne démarre pas (voir logs/${STAMP}-docker.log)."
    exit 1
  fi
fi

# En mode -p, Claude Code ignore les autorisations de .claude/settings.json tant que le dossier
# n'a pas été approuvé. Sur GitHub, on l'approuve ici ; sur un ordinateur, Ange l'a fait une fois.
CONFIG_CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME}/.claude.json"
if [ "$CYCLE" != "rapport" ]; then
  if [ -n "$EN_CLOUD" ]; then
    python3 - "$CONFIG_CLAUDE" "$(git rev-parse --show-toplevel)" <<'PY'
import json, sys
try:
    conf = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    conf = {}
conf["hasCompletedOnboarding"] = True
conf.setdefault("projects", {}).setdefault(sys.argv[2], {})["hasTrustDialogAccepted"] = True
json.dump(conf, open(sys.argv[1], "w"))
PY
  elif ! python3 - "$CONFIG_CLAUDE" "$(git rev-parse --show-toplevel)" <<'PY'
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
    exit 3
  fi
fi

STATUT=0
if [ "$CYCLE" != "rapport" ]; then
  # Le texte des sous-agents n'est transmis qu'avec une version récente de Claude Code
  OPTIONS_FLUX=(--output-format stream-json --verbose)
  if claude --help 2>/dev/null | grep -q -- "--forward-subagent-text"; then
    OPTIONS_FLUX+=(--forward-subagent-text)
  fi

  # Marqueur de début, utile à la salle de réunion
  printf '{"type":"cycle_start","cycle":"%s","started_at":"%s"}\n' "$CYCLE" "$(date -Iseconds)" > "$LOG"

  # Le cycle lui-même. timeout = garde-fou si une session ne s'arrête pas.
  INVITE="/cycle-$CYCLE"
  [ "$CYCLE" = "pilotage" ] && INVITE="/cycle-pilotage $SEMAINE"
  timeout 100m claude -p "$INVITE" \
    --permission-mode acceptEdits \
    --permission-prompts none \
    "${OPTIONS_FLUX[@]}" >> "$LOG" 2>> "logs/${STAMP}-${CYCLE}.err"
  STATUT=$?
  printf '{"type":"cycle_end","cycle":"%s","exit_code":%d,"ended_at":"%s"}\n' "$CYCLE" "$STATUT" "$(date -Iseconds)" >> "$LOG"

  # Les agents peuvent finir sur une branche de travail : on revient sur la branche principale
  # (les fichiers de state/ et reports/ modifiés suivent le changement de branche)
  git restore -q -- frontend/next-env.d.ts 2>/dev/null || true
  if [ "$(git branch --show-current)" != "$BRANCHE" ]; then
    git switch -q "$BRANCHE" || { notifier "Retour sur $BRANCHE impossible : à vérifier."; exit 1; }
  fi
fi

# Quota : on garde le dernier état connu pour le garde-fou et le rapport
if [ -f "$LOG" ]; then
  python3 - "$LOG" <<'PY'
import json, sys, time
dernier = None
for ligne in open(sys.argv[1], encoding="utf-8"):
    if '"rate_limit_event"' in ligne:
        try:
            dernier = json.loads(ligne)["rate_limit_info"]
        except (ValueError, KeyError):
            pass
if dernier and dernier.get("unifiedWindows"):
    q = dict(dernier["unifiedWindows"])
    q["status"] = dernier.get("status")
    q["maj"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    json.dump(q, open("state/quota.json", "w"), indent=2)
PY
fi

if [ "$STATUT" -ne 0 ]; then
  echo "| $(date +%F) | cycle-$CYCLE | - | coupé (code $STATUT) |" >> state/quota.md
fi

# Le portier merge les PR approuvées par qa, après avoir relancé lui-même toutes les vérifications
MERGES=""
if [ "$CYCLE" = "tech" ]; then
  MERGES="$(python3 scripts/portier.py 2>>"logs/${STAMP}-portier.log")"
  git switch -q "$BRANCHE" 2>/dev/null; git pull -q --ff-only
fi

# L'état de l'équipe est committé sur la branche principale par ce script, jamais par les agents
if [ -n "$(git status --porcelain -- state reports)" ]; then
  git add state reports
  git commit -q -m "État des agents : cycle $CYCLE du $(date +%F)"
  git push -q origin "$BRANCHE" || notifier "Push de l'état sur $BRANCHE refusé : vérifie la protection de branche."
fi

# Rapport PDF de la semaine (dimanche), publié sur GitHub avec le point hebdo pour Ange
if [ "$CYCLE" != "tech" ]; then
  python3 scripts/rapport.py --semaine "$SEMAINE" --publier 2>>"logs/${STAMP}-rapport.log" \
    || notifier "Rapport $SEMAINE non généré : voir logs/${STAMP}-rapport.log."
fi

# Journaux, captures et rapports vont sur la branche « livrables » (master reste léger)
scripts/publier-livrables.sh >/dev/null 2>>"logs/${STAMP}-livrables.log" || true

if [ "$STATUT" -eq 0 ]; then
  RESUME="$(grep '"type":"result"' "$LOG" 2>/dev/null | tail -1 | python3 -c 'import json,sys; print((json.loads(sys.stdin.read() or "{}").get("result") or "")[:500])' 2>/dev/null)"
  notifier "${MERGES:+$MERGES }${RESUME:-Cycle terminé.}"
else
  notifier "Cycle arrêté (code $STATUT) : quota atteint ou erreur. Le prochain cycle reprendra."
fi

exit "$STATUT"
