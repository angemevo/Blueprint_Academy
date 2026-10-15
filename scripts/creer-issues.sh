#!/usr/bin/env bash
# Crée les étiquettes et les issues de la phase 2b à partir du dossier issues/.
# Usage (depuis la racine du dépôt) : scripts/creer-issues.sh
# À lancer UNE seule fois : chaque exécution recrée les issues.

set -euo pipefail
cd "$(dirname "$0")/.."

gh label create ready      --color 0E8A16 --description "Prête : les agents peuvent la prendre" --force
gh label create a-cadrer   --color D93F0B --description "Décision d'Ange nécessaire avant développement" --force
gh label create phase-2b   --color 5319E7 --description "Backend : services, validateurs, API" --force
gh label create backend    --color 1D76DB --force
gh label create frontend   --color FBCA04 --force
gh label create outillage  --color C5DEF5 --force
gh label create story      --color BFD4F2 --force
gh label create bug        --color B60205 --force

declare -A NUMEROS
for fichier in issues/[0-9][0-9]-*.md; do
  titre="$(sed -n 's/^Titre: //p' "$fichier" | head -1)"
  labels="$(sed -n 's/^Labels: //p' "$fichier" | head -1)"
  corps="$(mktemp)"
  sed '1,/^---$/d' "$fichier" > "$corps"
  # Remplace les références #01, #02... par les vrais numéros d'issues déjà créées
  for cle in "${!NUMEROS[@]}"; do
    sed -i "s/#${cle}\b/#${NUMEROS[$cle]}/g" "$corps"
  done
  url="$(gh issue create --title "$titre" --label "$labels" --body-file "$corps")"
  rm -f "$corps"
  num="${url##*/}"
  NUMEROS["$(basename "$fichier" | cut -c1-2)"]="$num"
  echo "#$num  $titre"
done
