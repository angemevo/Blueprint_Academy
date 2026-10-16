#!/usr/bin/env bash
# Installe des voix françaises naturelles (Piper, synthèse neuronale locale) pour la salle de réunion.
# Usage : scripts/installer-voix.sh            2 voix (Jessica, Pierre), environ 140 Mo à télécharger
#         scripts/installer-voix.sh --complet  4 voix (+ Siwis, Tom),     environ 270 Mo à télécharger
# Une seule fois : tout reste ensuite sur ta machine, sans connexion.
set -euo pipefail
cd "$(dirname "$0")/.."
DOSSIER=outils/salle-reunion
VOIX=(fr_FR-upmc-medium)
if [ "${1:-}" = "--complet" ]; then
  VOIX+=(fr_FR-siwis-medium fr_FR-tom-medium)
fi

if ! python3 -c "import ensurepip" 2>/dev/null; then
  echo "Il manque le module venv de Python. Installe-le puis relance :"
  echo "  sudo apt install -y python3-venv"
  exit 1
fi

if [ ! -x "$DOSSIER/.venv/bin/python" ]; then
  echo "Création de l'environnement Python ($DOSSIER/.venv)…"
  python3 -m venv "$DOSSIER/.venv"
fi
echo "Installation de Piper (environ 70 Mo)…"
"$DOSSIER/.venv/bin/pip" install --quiet --disable-pip-version-check piper-tts

echo "Téléchargement des voix : ${VOIX[*]} (environ 63 Mo chacune)…"
"$DOSSIER/.venv/bin/python" -m piper.download_voices --download-dir "$DOSSIER/voix" "${VOIX[@]}"

echo
"$DOSSIER/.venv/bin/python" "$DOSSIER/serveur.py" --tester-voix
echo
echo "C'est prêt. Relance scripts/salle-reunion.sh et choisis « Voix naturelles (Piper) »."
