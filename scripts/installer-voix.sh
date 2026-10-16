#!/usr/bin/env bash
# Installe des voix françaises naturelles (Piper, synthèse neuronale locale) pour la salle de réunion.
# Usage : scripts/installer-voix.sh            2 voix (Jessica, Pierre), environ 140 Mo à télécharger
#         scripts/installer-voix.sh --complet  4 voix (+ Siwis, Tom),     environ 270 Mo à télécharger
# Une seule fois : tout reste ensuite sur ta machine, sans connexion.
# Pensé pour une connexion instable : on peut relancer le script, il reprend où il s'était arrêté.
set -euo pipefail
cd "$(dirname "$0")/.."
DOSSIER=outils/salle-reunion
VOIX=(fr_FR-upmc-medium)
if [ "${1:-}" = "--complet" ]; then
  VOIX+=(fr_FR-siwis-medium fr_FR-tom-medium)
fi
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR"

if ! python3 -c "import ensurepip" 2>/dev/null; then
  echo "Il manque le module venv de Python. Installe-le puis relance :"
  echo "  sudo apt install -y python3-venv"
  exit 1
fi

if [ ! -x "$DOSSIER/.venv/bin/python" ]; then
  echo "Création de l'environnement Python ($DOSSIER/.venv)…"
  python3 -m venv "$DOSSIER/.venv"
fi
PIP=("$DOSSIER/.venv/bin/pip" --disable-pip-version-check)

if ! "$DOSSIER/.venv/bin/python" -c "import piper" 2>/dev/null; then
  # Un pip récent sait reprendre un téléchargement interrompu (--resume-retries).
  echo "Mise à jour de pip (environ 2 Mo)…"
  "${PIP[@]}" install --quiet --timeout 60 --retries 10 --upgrade "pip>=25.1"
  echo "Installation de Piper (environ 70 Mo)…"
  for essai in 1 2 3; do
    if "${PIP[@]}" install --quiet --timeout 60 --retries 10 --resume-retries 20 piper-tts; then
      break
    fi
    [ "$essai" = 3 ] && { echo "Échec après 3 essais : relance le script quand le réseau sera meilleur."; exit 1; }
    echo "Connexion coupée, nouvel essai ($((essai + 1))/3)…"; sleep 5
  done
fi

mkdir -p "$DOSSIER/voix"
for voix in "${VOIX[@]}"; do
  nom="${voix#fr_FR-}"; nom="${nom%-medium}"
  for ext in onnx.json onnx; do
    fichier="$DOSSIER/voix/$voix.$ext"
    [ -s "$fichier" ] && continue
    echo "Téléchargement de $voix.$ext…"
    # -C - reprend un téléchargement partiel ; le fichier n'est renommé qu'une fois complet.
    curl -fL --retry 20 --retry-all-errors --retry-delay 3 --connect-timeout 30 \
      -C - -o "$fichier.part" "$BASE_URL/$nom/medium/$voix.$ext?download=true"
    mv "$fichier.part" "$fichier"
  done
done

echo
"$DOSSIER/.venv/bin/python" "$DOSSIER/serveur.py" --tester-voix
echo
echo "C'est prêt. Relance scripts/salle-reunion.sh : « Voix naturelles (Piper) » sera choisie par défaut."
