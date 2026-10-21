#!/usr/bin/env python3
"""Portier de l'équipe d'agents : merge les PR approuvées par qa, sans intervention d'Ange.

Ce script, et non un agent, décide du merge. Une PR n'est mergée que si :
  1. elle vient d'une branche feat/* ou fix/* du dépôt (pas d'un fork) ; une PR en brouillon
     approuvée par qa est d'abord passée en « prête » ;
  2. son dernier verdict, publié par l'équipe ou par Ange APRÈS le dernier commit, est
     « VERDICT : APPROUVÉE » ;
  3. elle ne touche aucun fichier protégé (sinon : étiquette a-valider-ange, Ange décide) ;
  4. elle reste petite (TAILLE_MAX lignes hors lockfiles et migrations) ;
  5. toutes les vérifications passent à nouveau, relancées ici sur le code de la PR fusionné
     avec master (ce qui sera réellement livré).
Le résultat s'affiche sur la PR comme une coche « Portier » verte ou rouge : c'est le contrôle
qui fait foi pour les PR de l'équipe (GitHub ne lance pas la CI sur les PR de son robot sans
l'approbation d'un humain).
Si une vérification échoue ou si la PR est en conflit, le portier publie « VERDICT : CORRECTIONS »
avec le détail : le developpeur reprend la PR au cycle suivant.

Usage : python3 scripts/portier.py [--essai]   (--essai : affiche les décisions sans rien faire)
Écrit sur la sortie standard une ligne de bilan (utilisée pour la notification).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
AUTEURS_DE_CONFIANCE = {"angemevo", "app/github-actions", "github-actions", "github-actions[bot]"}
FICHIERS_PROTEGES = re.compile(
    r"^(\.github/|\.claude/|scripts/|outils/|CLAUDE\.md$|docker-compose\.yml$|\.env)|(^|/)Dockerfile$"
)
HORS_TAILLE = re.compile(r"(package-lock\.json|/migrations/|\.lock$)")
TAILLE_MAX = 600
VERDICT = re.compile(r"^[\s*#>_]*VERDICT\s*:\s*(APPROUV|CORRECTIONS)", re.IGNORECASE)
LIVRAISONS = RACINE / "state" / "livraisons.md"


def lancer(cmd: list[str], timeout: int = 900) -> tuple[bool, str]:
    try:
        p = subprocess.run(cmd, cwd=RACINE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"délai dépassé ({timeout} s)"
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def gh_json(*args: str):
    ok, sortie = lancer(["gh", *args], timeout=120)
    if not ok:
        raise RuntimeError(sortie)
    return json.loads(sortie or "null")


def date(texte: str) -> dt.datetime:
    return dt.datetime.fromisoformat(texte.replace("Z", "+00:00"))


def dernier_verdict(pr: dict) -> str | None:
    """APPROUV, CORRECTIONS ou None, en ne gardant que les verdicts postérieurs au dernier commit."""
    if not pr["commits"]:
        return None
    dernier_commit = max(date(c["committedDate"]) for c in pr["commits"])
    messages = [(r.get("submittedAt"), r.get("body", ""), (r.get("author") or {}).get("login"))
                for r in pr["reviews"]]
    messages += [(c.get("createdAt"), c.get("body", ""), (c.get("author") or {}).get("login"))
                 for c in pr["comments"]]
    verdicts = []
    for quand, corps, auteur in messages:
        m = VERDICT.match(corps or "")
        if m and quand and auteur in AUTEURS_DE_CONFIANCE:
            verdicts.append((date(quand), m.group(1).upper()))
    if not verdicts:
        return None
    quand, verdict = max(verdicts)
    return verdict if quand >= dernier_commit else None


def verifications(fichiers: list[str]) -> list[tuple[str, list[str]]]:
    exe_b = ["docker", "compose", "exec", "-T", "backend"]
    exe_f = ["docker", "compose", "exec", "-T", "frontend"]
    etapes: list[tuple[str, list[str]]] = []
    if any(f.startswith("backend/requirements") for f in fichiers):
        etapes.append(("Dépendances Python", exe_b + ["pip", "install", "-q", "-r", "requirements-dev.txt"]))
    if any(f in ("frontend/package.json", "frontend/package-lock.json") for f in fichiers):
        etapes.append(("Dépendances frontend", exe_f + ["npm", "install", "--no-audit", "--no-fund"]))
    etapes.append(("Tests backend (pytest)", exe_b + ["pytest", "-q"]))
    if (RACINE / "backend" / "ruff.toml").exists():
        etapes.append(("Style Python (ruff)", exe_b + ["ruff", "check", "."]))
    etapes.append(("Migrations à jour", exe_b + ["python", "manage.py", "makemigrations", "--check", "--dry-run"]))
    etapes.append(("Types frontend", exe_f + ["npm", "run", "typecheck"]))
    if (RACINE / "frontend" / "eslint.config.mjs").exists():
        etapes.append(("Style frontend (ESLint)", exe_f + ["npm", "run", "lint"]))
    return etapes


def statut(sha: str, etat: str, description: str) -> None:
    """Coche « Portier » sur le dernier commit de la PR (success, failure ou pending)."""
    ok, depot = lancer(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], timeout=60)
    if ok and sha:
        lancer(["gh", "api", "-X", "POST", f"repos/{depot.strip()}/statuses/{sha}", "-f", f"state={etat}",
                "-f", "context=Portier (tests de l'équipe)", "-f", f"description={description[:140]}"], timeout=60)


def commenter(numero: int, corps: str) -> None:
    fichier = RACINE / "logs" / f"portier-{numero}.md"
    fichier.parent.mkdir(exist_ok=True)
    fichier.write_text(corps, encoding="utf-8")
    lancer(["gh", "pr", "comment", str(numero), "--body-file", str(fichier)])


def noter_livraison(pr: dict) -> None:
    if not LIVRAISONS.exists():
        LIVRAISONS.write_text(
            "# Livraisons\n\nÉcrit par `scripts/portier.py` à chaque merge. Lu par le rapport hebdo.\n\n"
            "| Date | PR | Titre | Issues |\n|---|---|---|---|\n", encoding="utf-8")
    issues = " ".join(f"#{i['number']}" for i in pr.get("closingIssuesReferences") or []) or "-"
    titre = pr["title"].replace("|", "/")
    with LIVRAISONS.open("a", encoding="utf-8") as f:
        f.write(f"| {dt.date.today().isoformat()} | #{pr['number']} | {titre} | {issues} |\n")


def lire_pr(numero: int) -> dict:
    champs = ("number,title,url,headRefName,headRefOid,isDraft,isCrossRepository,mergeable,files,"
              "commits,reviews,comments,labels,closingIssuesReferences")
    for _ in range(4):  # GitHub calcule « mergeable » en différé
        pr = gh_json("pr", "view", str(numero), "--json", champs)
        if pr["mergeable"] != "UNKNOWN":
            break
        time.sleep(5)
    return pr


def traiter(numero: int, essai: bool) -> str | None:
    pr = lire_pr(numero)
    if pr["isCrossRepository"] or not re.match(r"^(feat|fix)/", pr["headRefName"]):
        return None
    if dernier_verdict(pr) != "APPROUV":
        return None
    if pr["isDraft"]:
        # qa a approuvé : le brouillon n'a plus de raison d'être (les agents n'ont pas ce droit)
        if essai:
            return f"PR #{numero} serait passée en « prête » puis vérifiée."
        ok, sortie = lancer(["gh", "pr", "ready", str(numero)], timeout=60)
        if not ok:
            return f"PR #{numero} : impossible de la passer en « prête » ({sortie[:200]})."
    fichiers = [f["path"] for f in pr["files"]]
    etiquettes = {e["name"] for e in pr["labels"]}

    proteges = [f for f in fichiers if FICHIERS_PROTEGES.search(f)]
    taille = sum(f["additions"] + f["deletions"] for f in pr["files"] if not HORS_TAILLE.search(f["path"]))
    if proteges or taille > TAILLE_MAX:
        if "a-valider-ange" in etiquettes:
            return None
        raison = (f"elle touche des fichiers protégés ({', '.join(proteges[:5])})" if proteges
                  else f"elle fait {taille} lignes (maximum {TAILLE_MAX})")
        print(f"PR #{numero} : à valider par Ange, {raison}.", file=sys.stderr)
        if not essai:
            lancer(["gh", "label", "create", "a-valider-ange", "--color", "D93F0B", "--force",
                    "--description", "Le portier ne peut pas merger seul : décision d'Ange"])
            lancer(["gh", "pr", "edit", str(numero), "--add-label", "a-valider-ange"])
            commenter(numero, f"**Portier** : approuvée par qa, mais je ne la merge pas seul car {raison}. "
                              "Elle figure dans les questions du point hebdo.")
        return f"PR #{numero} en attente de ta décision."

    if pr["mergeable"] == "CONFLICTING":
        if not essai:
            commenter(numero, "VERDICT : CORRECTIONS (portier)\n\n1. La branche est en conflit avec `master` : "
                              "la mettre à jour (`git pull origin master`), résoudre les conflits, relancer "
                              "les vérifications et pousser.")
        return f"PR #{numero} en conflit, renvoyée au developpeur."

    print(f"PR #{numero} : approuvée, je relance les vérifications.", file=sys.stderr)
    if essai:
        return f"PR #{numero} serait vérifiée puis mergée."
    lancer(["git", "restore", "--", "frontend/next-env.d.ts"])  # réécrit par le serveur de dev
    statut(pr["headRefOid"], "pending", "Le portier relance toutes les vérifications")
    # pull/<n>/merge : la PR déjà fusionnée avec master par GitHub, c'est-à-dire ce qui sera livré
    ok, sortie = lancer(["git", "fetch", "-q", "origin", f"pull/{numero}/merge"])
    if not ok:
        ok, sortie = lancer(["git", "fetch", "-q", "origin", f"pull/{numero}/head"])
    # L'état de l'équipe (state/, reports/) peut être en cours d'écriture : on le met de côté le temps des tests
    ok_etat, etat = lancer(["git", "status", "--porcelain", "--", "state", "reports"])
    mis_de_cote = ok_etat and bool(etat.strip()) and lancer(
        ["git", "stash", "push", "-u", "-q", "-m", f"portier PR {numero}", "--", "state", "reports"])[0]
    ok = ok and lancer(["git", "switch", "-q", "--detach", "FETCH_HEAD"])[0]
    if not ok:
        if mis_de_cote:
            lancer(["git", "stash", "pop", "-q"])
        return f"PR #{numero} : impossible de récupérer le code ({sortie[:200]})."
    echecs = []
    try:
        for nom, cmd in verifications(fichiers):
            reussi, sortie = lancer(cmd)
            print(f"  {nom} : {'ok' if reussi else 'ÉCHEC'}", file=sys.stderr)
            if not reussi:
                echecs.append((nom, "\n".join(sortie.splitlines()[-40:])))
    finally:
        lancer(["git", "switch", "-q", "master"])
        if mis_de_cote:
            lancer(["git", "stash", "pop", "-q"])
        # Les dépendances installées pour la PR reviennent à celles de master
        for nom, cmd in verifications(fichiers):
            if nom.startswith("Dépendances"):
                lancer(cmd)

    if echecs:
        details = "\n\n".join(f"{i}. **{nom}** échoue :\n\n```\n{sortie}\n```"
                              for i, (nom, sortie) in enumerate(echecs, 1))
        commenter(numero, "VERDICT : CORRECTIONS (portier)\n\nqa avait approuvé, mais les vérifications "
                          f"relancées avant le merge (sur la PR fusionnée avec master) échouent :\n\n{details}")
        statut(pr["headRefOid"], "failure", "Échec : " + ", ".join(nom for nom, _ in echecs))
        return f"PR #{numero} : vérifications en échec, renvoyée au developpeur."

    statut(pr["headRefOid"], "success", "Tests, lint, types et migrations : tout passe")
    ok, sortie = lancer(["gh", "pr", "merge", str(numero), "--merge", "--delete-branch"], timeout=180)
    if not ok:
        return f"PR #{numero} : merge refusé par GitHub ({sortie[:200]})."
    noter_livraison(pr)
    return f"PR #{numero} mergée : {pr['title']}."


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge les PR approuvées par qa.")
    parser.add_argument("--essai", action="store_true", help="n'agit pas, affiche seulement")
    args = parser.parse_args()
    try:
        prs = gh_json("pr", "list", "--state", "open", "--limit", "20", "--json", "number")
    except RuntimeError as e:
        print(f"Portier : GitHub inaccessible ({e})", file=sys.stderr)
        return 1
    bilans = []
    for pr in sorted(prs, key=lambda p: p["number"]):
        try:
            bilan = traiter(pr["number"], args.essai)
        except (RuntimeError, KeyError, ValueError) as e:
            bilan = f"PR #{pr['number']} : erreur du portier ({e})."
        if bilan:
            bilans.append(bilan)
    print(" ".join(bilans))
    return 0


if __name__ == "__main__":
    sys.exit(main())
