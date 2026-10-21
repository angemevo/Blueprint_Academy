#!/usr/bin/env python3
"""Salle de réunion des agents : serveur local, sans dépendance.

Lit les journaux des cycles (logs/*.jsonl, écrits par scripts/cycle.sh) et les
sert à l'interface (index.html) :

- GET /                      l'interface
- GET /api/cycles            la liste des cycles enregistrés, du plus récent au plus ancien
- GET /api/journal?cycle=X   le contenu complet d'un cycle (X = nom de fichier ou "demo")
- GET /api/direct            flux en direct (Server-Sent Events) du cycle le plus récent,
                             qui bascule tout seul sur le cycle suivant quand il démarre

Usage : python3 outils/salle-reunion/serveur.py [--port 8765] [--logs CHEMIN]
Écoute uniquement sur 127.0.0.1 : rien n'est exposé sur le réseau.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import threading
import time
import wave
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ICI = Path(__file__).resolve().parent
DOSSIER_LOGS = ICI.parent.parent / "logs"
FICHIER_DEMO = ICI / "demo.jsonl"
INTERVALLE = 0.4  # secondes entre deux lectures du fichier suivi
BATTEMENT = 15  # secondes entre deux messages de maintien de connexion

# --- Voix naturelles (Piper, synthèse neuronale locale) -----------------------
# Installées par scripts/installer-voix.sh. Sans elles, l'interface se rabat sur la
# synthèse vocale du navigateur.
DOSSIER_VOIX = ICI / "voix"
CACHE_VOIX = ICI / ".cache-voix"
#: Pour chaque agent : modèles possibles par ordre de préférence
#: (nom du modèle, locuteur, vitesse : > 1 plus lent, < 1 plus rapide).
PROFILS_VOIX = {
    "pilote": [("fr_FR-siwis-medium", None, 1.0), ("fr_FR-upmc-medium", 0, 1.0)],
    "orchestrateur": [("fr_FR-tom-medium", None, 1.05), ("fr_FR-upmc-medium", 1, 1.1)],
    "organisateur": [("fr_FR-tom-medium", None, 1.05), ("fr_FR-upmc-medium", 1, 1.1)],
    "developpeur": [("fr_FR-upmc-medium", 1, 0.95)],
    "qa": [("fr_FR-upmc-medium", 0, 1.08), ("fr_FR-siwis-medium", None, 1.0)],
    "defaut": [("fr_FR-upmc-medium", 0, 1.0), ("fr_FR-siwis-medium", None, 1.0)],
}
try:
    from piper import PiperVoice, SynthesisConfig
except ImportError:  # Piper non installé : voix du navigateur
    PiperVoice = None
    SynthesisConfig = None


class Voix:
    """Charge les modèles Piper à la demande et met les phrases en cache disque."""

    def __init__(self) -> None:
        self.modeles: dict[str, object] = {}
        self.verrou = threading.Lock()

    def disponibles(self) -> list[str]:
        if PiperVoice is None:
            return []
        return sorted(p.name.removesuffix(".onnx") for p in DOSSIER_VOIX.glob("*.onnx"))

    def choisir(self, agent: str):
        presents = set(self.disponibles())
        for nom, locuteur, vitesse in PROFILS_VOIX.get(agent, []) + PROFILS_VOIX["defaut"]:
            if nom in presents:
                return nom, locuteur, vitesse
        return None

    def wav(self, agent: str, texte: str) -> bytes | None:
        choix = self.choisir(agent)
        if choix is None:
            return None
        nom, locuteur, vitesse = choix
        cle = hashlib.sha1(f"{nom}|{locuteur}|{vitesse}|{texte}".encode()).hexdigest()
        cache = CACHE_VOIX / f"{cle}.wav"
        if cache.exists():
            return cache.read_bytes()
        with self.verrou:  # un modèle ONNX n'aime pas les appels concurrents
            if nom not in self.modeles:
                self.modeles[nom] = PiperVoice.load(DOSSIER_VOIX / f"{nom}.onnx")
            tampon = io.BytesIO()
            with wave.open(tampon, "wb") as sortie:
                self.modeles[nom].synthesize_wav(
                    texte, sortie, syn_config=SynthesisConfig(speaker_id=locuteur, length_scale=vitesse)
                )
        donnees = tampon.getvalue()
        CACHE_VOIX.mkdir(exist_ok=True)
        cache.write_bytes(donnees)
        return donnees


VOIX = Voix()


def cycles(dossier: Path) -> list[Path]:
    """Journaux de cycle, du plus récent au plus ancien."""
    return sorted(dossier.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)


def resoudre(dossier: Path, nom: str) -> Path | None:
    """Chemin d'un journal à partir de son nom, sans sortir du dossier des logs."""
    if nom == "demo":
        return FICHIER_DEMO if FICHIER_DEMO.exists() else None
    candidat = (dossier / Path(nom).name).resolve()
    if candidat.parent != dossier.resolve() or candidat.suffix != ".jsonl":
        return None
    return candidat if candidat.exists() else None


def cycle_termine(chemin: Path) -> bool:
    """Le journal contient-il déjà la ligne de fin écrite par cycle.sh ?"""
    try:
        with chemin.open("rb") as f:
            f.seek(max(0, chemin.stat().st_size - 4096))
            return b'"cycle_end"' in f.read()
    except OSError:
        return True


class Gestionnaire(BaseHTTPRequestHandler):
    dossier_logs: Path = DOSSIER_LOGS
    server_version = "SalleReunion/1.0"

    def log_message(self, format, *args):  # noqa: A002 - signature imposée
        pass  # silencieux : l'interface a son propre journal

    # -- Réponses simples -------------------------------------------------
    def envoyer(self, statut: int, corps: bytes, type_contenu: str) -> None:
        self.send_response(statut)
        self.send_header("Content-Type", type_contenu)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)

    def envoyer_json(self, donnees, statut: int = 200) -> None:
        corps = json.dumps(donnees, ensure_ascii=False).encode()
        self.envoyer(statut, corps, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 - nom imposé par http.server
        url = urlparse(self.path)
        params = parse_qs(url.query)
        if url.path in ("/", "/index.html"):
            self.envoyer(200, (ICI / "index.html").read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/api/cycles":
            self.envoyer_json(
                [
                    {"nom": p.name, "modifie": p.stat().st_mtime, "taille": p.stat().st_size}
                    for p in cycles(self.dossier_logs)
                ]
            )
        elif url.path == "/api/journal":
            chemin = resoudre(self.dossier_logs, params.get("cycle", [""])[0])
            if chemin is None:
                self.envoyer_json({"erreur": "cycle introuvable"}, HTTPStatus.NOT_FOUND)
            else:
                self.envoyer(200, chemin.read_bytes(), "application/x-ndjson; charset=utf-8")
        elif url.path == "/api/direct":
            self.flux_direct()
        elif url.path == "/api/voix/etat":
            self.envoyer_json({"disponible": bool(VOIX.disponibles()), "modeles": VOIX.disponibles()})
        elif url.path == "/api/voix":
            texte = params.get("texte", [""])[0].strip()[:400]
            agent = params.get("agent", ["defaut"])[0]
            try:
                donnees = VOIX.wav(agent, texte) if texte else None
            except Exception as exc:  # modèle corrompu, texte impossible à phonétiser...
                self.envoyer_json({"erreur": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return
            if donnees is None:
                self.envoyer_json({"erreur": "voix Piper indisponible"}, HTTPStatus.NOT_FOUND)
            else:
                self.envoyer(200, donnees, "audio/wav")
        else:
            self.envoyer_json({"erreur": "introuvable"}, HTTPStatus.NOT_FOUND)

    # -- Flux en direct ---------------------------------------------------
    def evenement(self, nom: str, donnees) -> None:
        bloc = f"event: {nom}\ndata: {json.dumps(donnees, ensure_ascii=False)}\n\n"
        self.wfile.write(bloc.encode())
        self.wfile.flush()

    def flux_direct(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        courant: Path | None = None
        position = 0
        reste = b""
        dernier_battement = time.monotonic()
        try:
            while True:
                recents = cycles(self.dossier_logs)
                plus_recent = recents[0] if recents else None
                if plus_recent is not None and plus_recent != courant:
                    # Nouveau cycle : on l'annonce, puis on envoie tout ce qui est déjà écrit
                    # comme « rattrapage » (l'interface ne le lit pas à voix haute).
                    courant, position, reste = plus_recent, 0, b""
                    self.evenement("cycle", {"nom": courant.name, "termine": cycle_termine(courant)})
                    rattrapage = True
                else:
                    rattrapage = False
                if courant is not None:
                    with courant.open("rb") as f:
                        f.seek(position)
                        morceau = f.read()
                        position = f.tell()
                    if morceau:
                        lignes = (reste + morceau).split(b"\n")
                        reste = lignes.pop()  # ligne incomplète : attendre la suite
                        for ligne in lignes:
                            if ligne.strip():
                                self.evenement(
                                    "ligne",
                                    {"l": ligne.decode("utf-8", "replace"), "rattrapage": rattrapage},
                                )
                    if rattrapage:
                        self.evenement("direct", {"nom": courant.name})
                if time.monotonic() - dernier_battement > BATTEMENT:
                    self.wfile.write(b": battement\n\n")
                    self.wfile.flush()
                    dernier_battement = time.monotonic()
                time.sleep(INTERVALLE)
        except (BrokenPipeError, ConnectionResetError):
            return  # l'onglet a été fermé


def tester_voix() -> None:
    """Écrit un fichier WAV par agent dans outils/salle-reunion/test-voix/ et dit lequel écouter."""
    if PiperVoice is None:
        print("Piper n'est pas installé pour ce Python. Lance scripts/installer-voix.sh.")
        raise SystemExit(1)
    if not VOIX.disponibles():
        print(f"Aucun modèle de voix dans {DOSSIER_VOIX}. Lance scripts/installer-voix.sh.")
        raise SystemExit(1)
    dossier = ICI / "test-voix"
    dossier.mkdir(exist_ok=True)
    phrases = {
        "pilote": "Bonsoir à tous. On démarre le cycle tech : une issue ce soir.",
        "developpeur": "Les tests passent. J'ouvre la pull request.",
        "qa": "J'ai relu la PR. Verdict : approuvée.",
        "orchestrateur": "Le plan de la semaine est prêt. Deux issues au programme.",
        "organisateur": "Bonjour Ange. Le plan de la semaine est prêt, et la date de fin estimée est à jour.",
    }
    for agent, phrase in phrases.items():
        debut = time.monotonic()
        (dossier / f"{agent}.wav").write_bytes(VOIX.wav(agent, phrase))
        nom, locuteur, _ = VOIX.choisir(agent)
        detail = "" if locuteur is None else f" (locuteur {locuteur})"
        print(f"{agent:13s} {nom}{detail}  {time.monotonic() - debut:.1f} s")
    print(f"Écoute par exemple : aplay {dossier / 'developpeur.wav'}")


def main() -> None:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--port", type=int, default=8765)
    analyseur.add_argument("--logs", type=Path, default=DOSSIER_LOGS)
    analyseur.add_argument(
        "--tester-voix", action="store_true", help="synthétise une phrase par agent et quitte"
    )
    args = analyseur.parse_args()
    if args.tester_voix:
        tester_voix()
        return
    Gestionnaire.dossier_logs = args.logs.resolve()
    Gestionnaire.dossier_logs.mkdir(parents=True, exist_ok=True)
    serveur = ThreadingHTTPServer(("127.0.0.1", args.port), Gestionnaire)
    serveur.daemon_threads = True
    print(f"Salle de réunion ouverte : http://127.0.0.1:{args.port}  (Ctrl+C pour fermer)")
    print(f"Journaux lus dans : {Gestionnaire.dossier_logs}")
    modeles = VOIX.disponibles()
    print("Voix : " + (", ".join(modeles) if modeles else "celle du navigateur (scripts/installer-voix.sh pour des voix naturelles)"))
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nSalle fermée.")


if __name__ == "__main__":
    main()
