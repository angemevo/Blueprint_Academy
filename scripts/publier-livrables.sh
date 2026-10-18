#!/usr/bin/env bash
# Publie sur la branche « livrables » ce que l'équipe produit et qui n'a pas sa place dans le code :
#   journaux/  les cycles (fichiers .jsonl, rejouables dans la salle de réunion)
#   captures/  les captures d'écran et vidéos de qa, un dossier par PR (pr-<n>/)
#   rapports/  les rapports PDF hebdomadaires
# Appelé par scripts/cycle.sh à la fin de chaque cycle. master reste ainsi léger.
set -euo pipefail
cd "$(dirname "$0")/.."

BRANCHE=livrables
DOSSIER="$(mktemp -d)"
trap 'git worktree remove --force "$DOSSIER" >/dev/null 2>&1 || rm -rf "$DOSSIER"' EXIT

if git ls-remote --exit-code --heads origin "$BRANCHE" >/dev/null 2>&1; then
  git fetch -q origin "$BRANCHE"
  git worktree add -q --detach "$DOSSIER" "origin/$BRANCHE"
else
  git worktree add -q --detach "$DOSSIER" HEAD
  git -C "$DOSSIER" checkout -q --orphan "$BRANCHE-nouvelle"
  git -C "$DOSSIER" rm -rqf --ignore-unmatch .
  cat > "$DOSSIER/README.md" <<'EOF'
# Livrables de l'équipe d'agents

Branche écrite automatiquement par `scripts/publier-livrables.sh`. Ne pas modifier à la main.

- `rapports/` : rapports PDF hebdomadaires
- `captures/pr-<n>/` : captures d'écran et vidéo de chaque PR relue par qa
- `journaux/` : journaux des cycles, à rejouer dans la salle de réunion (`scripts/salle-reunion.sh`)
EOF
fi

mkdir -p "$DOSSIER/journaux" "$DOSSIER/captures" "$DOSSIER/rapports"
for f in logs/*.jsonl; do
  [ -e "$f" ] || continue
  [ -e "$DOSSIER/journaux/$(basename "$f")" ] || cp "$f" "$DOSSIER/journaux/"
done
if [ -d logs/captures ]; then
  cp -r logs/captures/. "$DOSSIER/captures/"
fi
if [ -d logs/rapports ]; then
  cp -r logs/rapports/. "$DOSSIER/rapports/"
fi

git -C "$DOSSIER" add -A
if git -C "$DOSSIER" diff --cached --quiet; then
  exit 0
fi
git -C "$DOSSIER" commit -q -m "Livrables du $(date +%F_%H%M)"
git -C "$DOSSIER" push -q origin "HEAD:refs/heads/$BRANCHE"
