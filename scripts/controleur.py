#!/usr/bin/env python3
"""Contrôleur d'actions de l'équipe d'agents (hook PreToolUse de Claude Code).

Il valide chaque action d'un agent à la place d'Ange, instantanément, pour que plus rien
n'attende une approbation pendant la nuit :
  - ce qui est sûr est accepté tout de suite (« allow ») ;
  - ce qui est dangereux est refusé avec une raison et la marche à suivre (« deny »),
    l'agent s'adapte et continue.
Les règles « deny » de .claude/settings.json s'appliquent en plus : Claude Code les
vérifie quoi que réponde ce contrôleur.

Entrée : le JSON du hook sur stdin. Sortie : la décision en JSON sur stdout.
Chaque refus est noté dans logs/controleur.jsonl (lu par le rapport du matin).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Fichiers que les agents ne modifient jamais (CLAUDE.md, règles de l'équipe, scripts, CI…)
PROTEGES = re.compile(
    r"(^|/)(\.github/|\.claude/|scripts/|outils/|CLAUDE\.md\b|docker-compose\.ya?ml\b|Dockerfile\b|\.gitattributes\b)"
)
SECRETS = re.compile(
    r"\.env(?!\.example)(?![\w-])|CLAUDE_CODE_OAUTH_TOKEN|\bGH_TOKEN\b|GITHUB_TOKEN|NTFY_TOPIC|ACTIONS_RUNTIME"
    r"|\bprintenv\b|/proc/[^\s]*/environ|\bexport\s+-p\b|\bdeclare\s+-[a-zA-Z]*x|\.claude\.json|\.credentials"
    r"|\.git-credentials|\bgh\s+auth\b|\.ssh/|\bid_rsa\b"
)

# (motif, raison donnée à l'agent)
REFUS_BASH: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(^|[;&|(]\s*)env\s*($|[;&|>])|(^|[;&|]\s*)set\s*($|[;&|])"),
     "afficher les variables d'environnement pourrait révéler un secret."),
    (SECRETS, "cette commande touche à un secret (.env, jetons, identifiants) : interdit."),
    (re.compile(r"\bdocker\s+compose\s+down\b|\bdocker\s+(volume|system|rm|rmi|kill)\b|\bdocker\s+compose\s+rm\b"),
     "la stack Docker et ses données ne se suppriment pas. Pour relancer un service : "
     "docker compose restart <service>."),
    (re.compile(r"manage\.py\s+(flush|shell|dbshell|sqlflush|reset_db)\b"), "vider ou ouvrir la base à la main est interdit."),
    (re.compile(r"\bsudo\b|\bapt(-get)?\b|\bsnap\b|\bsystemctl\b|\bcrontab\b|\bchown\b"),
     "pas d'administration de la machine : tout passe par les conteneurs Docker."),
    (re.compile(r"\b(pkill|killall)\b|\bkill\s+-9\b|\bkill\s+-1\b|\bkill\s+-[A-Z]+\s+-1\b"),
     "ne tue pas de processus : relance le service concerné avec docker compose restart."),
    (re.compile(r"\bgit\s+push\b[^\n]*(\s(-f|--force|--force-with-lease|--mirror|--delete)\b|\s\+)"),
     "jamais de push forcé ni de suppression de branche distante."),
    (re.compile(r"\bgit\s+push\b[^\n]*\b(master|main)\b"),
     "on ne pousse jamais sur master : pousse ta branche feat/… ou fix/… et ouvre une PR."),
    (re.compile(r"\bgit\s+(reset\s+--hard|clean\b|filter-branch|update-ref|replace)\b|\bgit\s+config\b(?!\s+--get)"),
     "commande git destructive ou qui change la configuration : interdite. "
     "Pour annuler un fichier : git restore <fichier>."),
    (re.compile(r"\bgit\s+(-C|--git-dir|--work-tree)\b"), "lance git depuis la racine du dépôt, sans -C."),
    (re.compile(r"\bgh\s+(pr\s+merge|release|secret|variable|repo|workflow|run|api|auth|ssh-key|gpg-key|cache|ruleset)\b"),
     "réservé au portier ou à Ange. Le portier merge seul les PR approuvées par qa."),
    (re.compile(r"\bgh\s+(issue|pr|label)\s+delete\b"), "on ne supprime rien sur GitHub : ferme l'issue avec une explication."),
    (re.compile(r"\bgh\s+(pr|issue)\s+edit\b[^\n]*(a-valider-ange|point-hebdo|bureau)"),
     "ces étiquettes sont réservées au portier, à l'organisateur et à Ange."),
    (re.compile(r"\b(curl|wget|nc|ncat|netcat|ssh|scp|sftp|ftp|telnet|rsync)\b"),
     "pas d'accès réseau direct : GitHub passe par gh, les paquets par npm/pip dans les conteneurs."),
    (re.compile(r"(^|[;&|]\s*)(python3?|node|perl|ruby)\s+-(c|e)\b"),
     "pas de script improvisé sur la machine. Pour lire du JSON : jq, ou les options --json/--jq de gh ; "
     "pour du code Python du projet : docker compose exec -T backend …"),
    (re.compile(r"(^|[;&|]\s*)(npx|npm|pip3?|pipx|uv)\s"),
     "installe et lance les outils dans les conteneurs : docker compose exec -T frontend npx …, "
     "docker compose exec -T backend pip …"),
    (re.compile(r"\brm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+(/|~|\.|\*|\.\.)(\s|$)"), "suppression trop large : supprime les fichiers un par un."),
]
# Une commande qui écrit (verbe en tête de segment, ou redirection) ne vise jamais un fichier protégé
PROTEGES_CMD = re.compile(
    r"(^|[\s'\"=/])(\.github/|\.claude/|scripts/|outils/|CLAUDE\.md\b|docker-compose\.ya?ml\b|Dockerfile\b|\.gitattributes\b)"
)
ECRITURE = re.compile(
    r"^\s*(sudo\s+)?(sed\s+(-[a-zA-Z]*\s+)*-i|tee|mv|cp|rm|truncate|chmod|ln|install|patch|dd|touch|mkdir"
    r"|git\s+(rm|mv|checkout|restore|apply|am|add))\b"
)
REDIRECTION = re.compile(r"(?<![0-9&])>{1,2}\s*([^\s;&|)]+)")
SEPARATEURS = re.compile(r"&&|\|\||[;|\n]")


def decision(choix: str, raison: str = "") -> None:
    sortie = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": choix}}
    if raison:
        sortie["hookSpecificOutput"]["permissionDecisionReason"] = raison
    print(json.dumps(sortie, ensure_ascii=False))


def noter_refus(entree: dict, raison: str) -> None:
    try:
        (RACINE / "logs").mkdir(exist_ok=True)
        with (RACINE / "logs" / "controleur.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"outil": entree.get("tool_name"), "agent": entree.get("agent_type") or "chef",
                                "entree": json.dumps(entree.get("tool_input"), ensure_ascii=False)[:300],
                                "raison": raison}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def relatif(chemin: str, cwd: str) -> str | None:
    """Chemin relatif à la racine du dépôt, ou None s'il est en dehors."""
    p = Path(chemin)
    if not p.is_absolute():
        p = Path(cwd or RACINE) / p
    try:
        return p.resolve().relative_to(RACINE.resolve()).as_posix()
    except ValueError:
        return None


def juger_bash(commande: str) -> str | None:
    for motif, raison in REFUS_BASH:
        if motif.search(commande):
            return raison
    cibles = REDIRECTION.findall(commande)
    segments = SEPARATEURS.split(commande)
    if any(PROTEGES_CMD.search(" " + c) for c in cibles) or any(
            ECRITURE.search(seg) and PROTEGES_CMD.search(seg) for seg in segments):
        return ("ce fichier est protégé (règles de l'équipe, scripts, CI, CLAUDE.md, Docker) : "
                "seul Ange le modifie. Si la tâche l'exige, note-le dans la PR et passe à la suite.")
    return None


def juger_fichier(outil: str, entree: dict, agent: str) -> str | None:
    chemin = entree.get("file_path") or entree.get("notebook_path") or entree.get("path") or ""
    if not chemin:
        return None
    if SECRETS.search(chemin):
        return "ce fichier contient des secrets : interdit."
    if outil in ("Read", "Grep", "Glob"):
        return None
    rel = relatif(chemin, entree.get("_cwd", ""))
    if rel is None:
        return "écris uniquement dans le dépôt ; les brouillons vont dans logs/."
    if PROTEGES.search(rel):
        return ("ce fichier est protégé (règles de l'équipe, scripts, CI, CLAUDE.md, Docker) : seul Ange le modifie.")
    if agent == "qa" and not rel.startswith("logs/"):
        return "qa ne modifie pas le code : écris ta revue et tes scénarios dans logs/."
    return None


def main() -> int:
    try:
        entree = json.load(sys.stdin)
    except ValueError:
        return 0  # rien à juger : Claude Code applique ses règles habituelles
    outil = entree.get("tool_name", "")
    params = dict(entree.get("tool_input") or {})
    params["_cwd"] = entree.get("cwd", "")
    agent = entree.get("agent_type") or ""

    if outil == "Bash":
        raison = juger_bash(params.get("command", ""))
    elif outil in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep", "Glob"):
        raison = juger_fichier(outil, params, agent)
    else:
        return 0  # Agent, TodoWrite, WebFetch… : circuit normal

    if raison:
        noter_refus(entree, raison)
        decision("deny", f"Refusé par le contrôleur de l'équipe : {raison}")
    else:
        decision("allow")
    return 0


if __name__ == "__main__":
    sys.exit(main())
