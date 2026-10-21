"""Outils partagés par les scripts de l'équipe d'agents (bibliothèque standard seulement)."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = RACINE / "state"
LOGS = RACINE / "logs"
ANGE = "angemevo"
EQUIPE = {"github-actions", "github-actions[bot]", "app/github-actions"}

JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]


def lancer(cmd: list[str], timeout: int = 300, entree: str | None = None) -> tuple[bool, str]:
    """Lance une commande depuis la racine du dépôt ; renvoie (réussi, sortie + erreurs)."""
    try:
        p = subprocess.run(cmd, cwd=RACINE, capture_output=True, text=True, timeout=timeout, input=entree)
    except subprocess.TimeoutExpired:
        return False, f"délai dépassé ({timeout} s) : {' '.join(cmd[:4])}"
    except FileNotFoundError:
        return False, f"commande introuvable : {cmd[0]}"
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def gh_json(*args: str, timeout: int = 120):
    p = subprocess.run(["gh", *args], cwd=RACINE, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or f"gh {' '.join(args[:3])} a échoué")
    return json.loads(p.stdout or "null")


def lire_json(chemin: Path, defaut):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return defaut


def ecrire_json(chemin: Path, donnees) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_suffix(chemin.suffix + ".tmp")
    tmp.write_text(json.dumps(donnees, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(chemin)


def maintenant() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def date_iso(texte: str) -> dt.datetime:
    return dt.datetime.fromisoformat(texte.replace("Z", "+00:00"))


def jour_fr(d: dt.date, avec_jour: bool = True) -> str:
    texte = f"{d.day if d.day > 1 else '1er'} {MOIS[d.month - 1]}"
    return f"{JOURS[d.weekday()]} {texte}" if avec_jour else texte


def heure_fr(t: dt.datetime) -> str:
    return f"{t.hour} h {t.minute:02d}"


def cle_nuit(t: dt.datetime | None = None) -> str:
    """Une nuit de travail porte la date du soir où elle commence (avant midi : la veille)."""
    t = t or maintenant()
    jour = t.date() - dt.timedelta(days=1) if t.hour < 12 else t.date()
    return jour.isoformat()


def notifier(titre: str, message: str) -> None:
    """Notification téléphone (ntfy) si NTFY_TOPIC est défini ; toujours affichée dans le journal."""
    print(f"[notification] {titre} : {message}", flush=True)
    sujet = os.environ.get("NTFY_TOPIC")
    if not sujet:
        return
    try:
        req = urllib.request.Request(f"https://ntfy.sh/{sujet}", data=message[:3000].encode(),
                                     headers={"Title": titre.encode("latin-1", "replace").decode("latin-1")})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:  # noqa: BLE001 - une notification ratée ne doit rien arrêter
        print(f"[notification] échec : {e}", flush=True)
