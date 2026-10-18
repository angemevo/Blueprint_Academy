#!/usr/bin/env python3
"""Captures d'écran et vidéo d'une PR, pour montrer à Ange ce qui a changé.

qa écrit un scénario JSON, puis lance : python3 scripts/captures.py logs/captures/pr-<n>/scenario.json
Le script joue le scénario dans un vrai navigateur (Chromium), filme tout le parcours et enregistre,
dans le dossier du scénario : 01-<nom>.png, 02-…, video.webm et resultat.json.

Format du scénario :
{
  "titre": "Créer un exercice QCM depuis l'admin",
  "connexion_admin": true,                       # connecte un compte d'admin de démonstration
  "etapes": [
    {"aller": "/admin/exercises/exercise/add/"},  # /admin et /api → backend, sinon → frontend
    {"remplir": "#id_title", "texte": "Mon QCM"},
    {"choisir": "#id_type", "valeur": "B"},
    {"cliquer": "text=Enregistrer"},
    {"attendre": 1500},
    {"capture": "Le message d'erreur explique ce qui manque"},
    {"capture": "Page entière", "pleine_page": true}
  ]
}
Chaque légende de capture est écrite pour Ange, qui ne lit pas le code : dire ce qu'on voit
et pourquoi c'est utile pour un étudiant ou un formateur.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FRONT = os.environ.get("CAPTURES_FRONT", "http://localhost:3000")
API = os.environ.get("CAPTURES_API", "http://localhost:8000")
ADMIN = {"utilisateur": "demo", "mot_de_passe": "demo-captures-2026", "email": "demo@example.com"}
DELAI_PAGE = 90_000  # le serveur de dev de Next compile une page à sa première visite
DELAI_ACTION = 15_000


def adresse(chemin: str) -> str:
    if chemin.startswith("http"):
        return chemin
    base = API if re.match(r"^/(admin|api)(/|$)", chemin) else FRONT
    return base + chemin


def nom_fichier(n: int, legende: str) -> str:
    s = unicodedata.normalize("NFKD", legende).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()[:40] or "capture"
    return f"{n:02d}-{s}.png"


def creer_admin_demo() -> None:
    env = ["-e", f"DJANGO_SUPERUSER_USERNAME={ADMIN['utilisateur']}",
           "-e", f"DJANGO_SUPERUSER_PASSWORD={ADMIN['mot_de_passe']}",
           "-e", f"DJANGO_SUPERUSER_EMAIL={ADMIN['email']}"]
    subprocess.run(["docker", "compose", "exec", "-T", *env, "backend",
                    "python", "manage.py", "createsuperuser", "--noinput"],
                   cwd=RACINE, capture_output=True, text=True, timeout=120)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    scenario_fichier = Path(sys.argv[1]).resolve()
    dossier = scenario_fichier.parent
    if RACINE / "logs" not in scenario_fichier.parents:
        print("Le scénario doit être dans logs/captures/pr-<n>/.", file=sys.stderr)
        return 2
    scenario = json.loads(scenario_fichier.read_text(encoding="utf-8"))
    try:
        from playwright.sync_api import Error as ErreurPlaywright
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright n'est pas installé ici : captures impossibles. Sur GitHub, il est installé "
              "par le workflow. Note-le dans la revue (« captures non faites »).", file=sys.stderr)
        return 3

    if scenario.get("connexion_admin"):
        creer_admin_demo()

    resultat = {"titre": scenario.get("titre", ""), "date": time.strftime("%Y-%m-%d %H:%M"),
                "captures": [], "video": None, "erreurs": []}
    numero = 0
    with sync_playwright() as p:
        navigateur = p.chromium.launch()
        contexte = navigateur.new_context(viewport={"width": 1280, "height": 720}, locale="fr-FR",
                                          record_video_dir=str(dossier / "video-brute"),
                                          record_video_size={"width": 1280, "height": 720})
        contexte.set_default_timeout(DELAI_ACTION)
        contexte.set_default_navigation_timeout(DELAI_PAGE)
        page = contexte.new_page()
        if scenario.get("connexion_admin"):
            try:
                page.goto(adresse("/admin/login/"))
                page.fill("#id_username", ADMIN["utilisateur"])
                page.fill("#id_password", ADMIN["mot_de_passe"])
                page.click("input[type=submit]")
                page.wait_for_load_state()
            except ErreurPlaywright as e:
                resultat["erreurs"].append(f"connexion à l'admin : {str(e).splitlines()[0]}")
        for i, etape in enumerate(scenario.get("etapes", []), 1):
            try:
                if "aller" in etape:
                    page.goto(adresse(etape["aller"]))
                    try:
                        page.wait_for_load_state("networkidle", timeout=10_000)
                    except ErreurPlaywright:
                        pass  # une page qui garde une connexion ouverte reste utilisable
                elif "cliquer" in etape:
                    page.click(etape["cliquer"])
                    page.wait_for_load_state()
                elif "remplir" in etape:
                    page.fill(etape["remplir"], str(etape.get("texte", "")))
                elif "choisir" in etape:
                    page.select_option(etape["choisir"], str(etape.get("valeur", "")))
                elif "attendre" in etape:
                    page.wait_for_timeout(min(int(etape["attendre"]), 10_000))
                elif "capture" in etape:
                    numero += 1
                    fichier = nom_fichier(numero, etape["capture"])
                    page.wait_for_timeout(400)
                    page.screenshot(path=str(dossier / fichier), full_page=bool(etape.get("pleine_page")))
                    resultat["captures"].append({"fichier": fichier, "legende": etape["capture"],
                                                 "adresse": page.url})
                else:
                    resultat["erreurs"].append(f"étape {i} inconnue : {etape}")
            except ErreurPlaywright as e:
                resultat["erreurs"].append(f"étape {i} ({next(iter(etape))}) : {str(e).splitlines()[0]}")
        page.wait_for_timeout(800)
        video = page.video
        contexte.close()
        navigateur.close()
        if video:
            brute = Path(video.path())
            brute.replace(dossier / "video.webm")
            resultat["video"] = "video.webm"
        brut = dossier / "video-brute"
        if brut.is_dir():
            for f in brut.iterdir():
                f.unlink()
            brut.rmdir()

    (dossier / "resultat.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(resultat['captures'])} capture(s), vidéo : {'oui' if resultat['video'] else 'non'}, "
          f"erreurs : {len(resultat['erreurs'])}")
    for e in resultat["erreurs"]:
        print("  - " + e)
    return 0 if not resultat["erreurs"] else 1


if __name__ == "__main__":
    sys.exit(main())
