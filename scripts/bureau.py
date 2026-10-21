#!/usr/bin/env python3
"""Le bureau de l'organisateur : le seul fil de discussion entre Ange et l'équipe.

Une issue GitHub par semaine, étiquetée « bureau », assignée à Ange :
  - le dimanche, l'organisateur y publie le rapport PDF de la semaine et ses questions ;
  - chaque matin, le rapport de la nuit (scripts/bureau.py matin) ;
  - à tout moment, Ange y écrit en commentaire ; l'organisateur répond (cycle « courrier »).

Usage :
  python3 scripts/bureau.py ouvrir            # numéro du bureau en cours (créé s'il manque)
  python3 scripts/bureau.py courrier          # écrit logs/courrier.md ; code 1 si rien de nouveau
  python3 scripts/bureau.py matin [--essai]   # publie le rapport des nuits non encore rapportées
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys

from commun import ANGE, ETAT, LOGS, date_iso, ecrire_json, gh_json, heure_fr, jour_fr, lancer, lire_json

LABEL = "bureau"
SIGNATURE = "\n\n— *L'organisateur de l'équipe*\n<!-- organisateur -->"
COURRIER = ETAT / "courrier.json"
NUITS = ETAT / "nuits"
TYPES = {"dev": "Développement", "reprise": "Corrections", "revue": "Relecture", "auto": "Tâche au choix du chef"}
STATUTS = {"fait": "✅ terminé", "bloque": "⛔ bloqué", "echec": "⚠️ échec", "delai": "⏱ temps dépassé",
           "quota": "⏸ arrêté (quota)", "a_faire": "⏳ pas commencé", "en_cours": "en cours", "reporte": "↪ reporté"}

INTRO = """Bonjour Ange,

Ce fil est **mon bureau** pour la semaine : c'est ici, et seulement ici, que tu parles à l'équipe.

- **Écris-moi en commentaire, quand tu veux** : une question (« où en est-on ? », « quand ce sera fini ? »), une consigne (« passe l'inscription en premier »), une réponse à mes questions (« Q1 : A »). Je te réponds ici en quelques minutes, ou au plus tard entre deux créneaux de la nuit.
- **Chaque matin**, je publie ici le rapport de la nuit : ce qui a été fait, les incidents et comment l'équipe les a réglés, l'avancement et la date de fin estimée.
- **Chaque dimanche soir**, le rapport PDF de la semaine, avec captures et vidéos.

Tu n'as rien d'autre à surveiller : le chef d'équipe distribue le travail, le contrôleur valide les actions, le portier livre ce qui est relu et testé."""


def lundi_de(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())


def titre_semaine(lundi: dt.date) -> str:
    return f"Bureau de l'organisateur · semaine du {jour_fr(lundi, avec_jour=False)}"


def bureaux_ouverts() -> list[dict]:
    return gh_json("issue", "list", "--label", LABEL, "--state", "open", "--limit", "10",
                   "--json", "number,title,createdAt")


def ouvrir(lundi: dt.date | None = None, corps_extra: str = "") -> int:
    """Numéro du bureau de la semaine. Sans `lundi` : le plus récent ouvert, sinon celui de cette semaine."""
    lancer(["gh", "label", "create", LABEL, "--color", "3D5AFE", "--force",
            "--description", "Le bureau de l'organisateur : le fil entre Ange et l'équipe d'agents"])
    ouverts = bureaux_ouverts()
    if lundi is None:
        if ouverts:
            return max(ouverts, key=lambda i: i["createdAt"])["number"]
        lundi = lundi_de(dt.date.today())
    titre = titre_semaine(lundi)
    meme = [i for i in ouverts if i["title"] == titre]
    corps = INTRO + ("\n\n" + corps_extra if corps_extra else "")
    fichier = LOGS / "bureau-corps.md"
    LOGS.mkdir(exist_ok=True)
    fichier.write_text(corps + SIGNATURE, encoding="utf-8")
    if meme:
        numero = meme[0]["number"]
        if corps_extra:
            lancer(["gh", "issue", "edit", str(numero), "--body-file", str(fichier)])
    else:
        ok, sortie = lancer(["gh", "issue", "create", "--title", titre, "--label", LABEL,
                             "--assignee", ANGE, "--body-file", str(fichier)])
        if not ok:
            raise RuntimeError(f"création du bureau impossible : {sortie[:300]}")
        numero = int(sortie.strip().rstrip("/").split("/")[-1])
    for i in ouverts:
        if i["number"] != numero:
            # Les messages non lus de l'ancien bureau restent traités : le courrier lit aussi l'ancien
            lancer(["gh", "issue", "close", str(i["number"]), "--comment",
                    f"La semaine continue dans le nouveau bureau : #{numero}." + SIGNATURE])
    return numero


def poster(numero: int, texte: str) -> bool:
    fichier = LOGS / f"bureau-{numero}-message.md"
    fichier.write_text(texte.rstrip() + SIGNATURE, encoding="utf-8")
    ok, sortie = lancer(["gh", "issue", "comment", str(numero), "--body-file", str(fichier)])
    if not ok:
        print(f"Publication dans le bureau #{numero} impossible : {sortie[:300]}", file=sys.stderr)
    return ok


# ---------------------------------------------------------------------------
# Courrier : les messages d'Ange auxquels l'organisateur n'a pas encore répondu
# ---------------------------------------------------------------------------
def nouveaux_messages() -> list[dict]:
    deja = set(lire_json(COURRIER, {}).get("repondus", []))
    numeros = [i["number"] for i in bureaux_ouverts()]
    # Le bureau de la semaine passée, fermé dimanche, peut contenir un message tardif
    fermes = gh_json("issue", "list", "--label", LABEL, "--state", "closed", "--limit", "1", "--json", "number")
    numeros += [i["number"] for i in fermes]
    messages = []
    for n in numeros:
        for c in gh_json("issue", "view", str(n), "--json", "comments")["comments"]:
            if (c.get("author") or {}).get("login") == ANGE and c["url"] not in deja:
                messages.append({"bureau": n, "url": c["url"], "date": c["createdAt"], "texte": c["body"]})
    return sorted(messages, key=lambda m: m["date"])


def preparer_courrier() -> list[dict]:
    messages = nouveaux_messages()
    if not messages:
        return []
    lignes = ["# Messages d'Ange en attente de réponse", ""]
    for m in messages:
        t = date_iso(m["date"])
        lignes += [f"## Message du {jour_fr(t.date())} à {heure_fr(t)} (bureau #{m['bureau']})", "", m["texte"], ""]
    (LOGS / "courrier.md").write_text("\n".join(lignes), encoding="utf-8")
    return messages


def marquer_repondus(messages: list[dict]) -> None:
    etat = lire_json(COURRIER, {"repondus": []})
    etat["repondus"] = (etat.get("repondus", []) + [m["url"] for m in messages])[-300:]
    ecrire_json(COURRIER, etat)


# ---------------------------------------------------------------------------
# Rapport du matin
# ---------------------------------------------------------------------------
def questions_en_attente() -> list[str]:
    try:
        texte = (ETAT / "validations.md").read_text(encoding="utf-8")
    except OSError:
        return []
    bloc = texte.split("## En attente", 1)[-1].split("\n## ", 1)[0]
    return [re.sub(r"\*\*", "", m).rstrip(". ") for m in re.findall(r"^- \[ \] (\*\*[^*]+\*\*)", bloc, re.M)]


def titre_nuit(cle: str) -> str:
    soir = dt.date.fromisoformat(cle)
    lendemain = soir + dt.timedelta(days=1)
    return f"nuit du {jour_fr(soir)} au {jour_fr(lendemain)}"


def rapport_nuits(nuits: list[dict], avancement_texte: str, quota: dict) -> str:
    h = []
    for nuit in nuits:
        creneaux = nuit.get("creneaux", [])
        faits = [c for c in creneaux if c.get("statut") == "fait"]
        minutes = sum(c.get("minutes_reelles", 0) for c in creneaux)
        h.append(f"## ☀️ Rapport de la {titre_nuit(nuit['nuit'])}")
        if not creneaux:
            raisons = [i["texte"] for i in nuit.get("incidents", [])] or ["aucune tâche prête"]
            h += ["", f"L'équipe n'a pas travaillé cette nuit : {raisons[-1]}"]
        else:
            h += ["", f"**En bref :** {len(faits)} créneau(x) terminé(s) sur {len(creneaux)} (relances comprises), "
                      f"{len(nuit.get('merges', []))} livraison(s), {len(nuit.get('incidents', []))} incident(s), "
                      f"{minutes // 60} h {minutes % 60:02d} de travail."]
        if nuit.get("merges"):
            h += ["", "**Livré cette nuit** (vérifié, relu, mis dans le site) :"]
            h += [f"- {m['texte']}" for m in nuit["merges"]]
        if creneaux:
            h += ["", "**Le planning du chef d'équipe et ce qu'il est devenu :**", "",
                  "| Créneau | Tâche | Résultat |", "|---|---|---|"]
            for c in creneaux:
                debut = date_iso(c["debut"]) if c.get("debut") else None
                quand = f"{heure_fr(debut)} · " if debut else ""
                tache = f"{TYPES.get(c.get('type'), c.get('type', ''))} : {c.get('titre') or c.get('cible', '')}"
                resume = (c.get("resume") or c.get("dernier_probleme") or "").replace("\n", " ").replace("|", "/")[:400]
                h.append(f"| {quand}{c.get('minutes', '?')} min | {tache} | "
                         f"{STATUTS.get(c.get('statut'), c.get('statut', ''))}{' — ' + resume if resume else ''} |")
        if nuit.get("incidents"):
            h += ["", "**Incidents, et ce que l'équipe a fait :**"]
            h += [f"- {i['texte']}" for i in nuit["incidents"]]
        h.append("")
    h += ["## Où en est le projet", "", avancement_texte, ""]
    questions = questions_en_attente()
    if questions:
        h += [f"**{len(questions)} question(s) t'attendent** (détail dans le dernier rapport du dimanche) : "
              + " ; ".join(questions) + ". Réponds-moi ici, par exemple « Q1 : A »."]
    else:
        h.append("Aucune décision ne t'attend.")
    sept = (quota.get("seven_day") or {}).get("utilization")
    if sept is not None:
        h.append(f"\nQuota Claude utilisé cette semaine (toi et l'équipe) : {round(sept * 100)} %.")
    return "\n".join(h)


def matin(essai: bool = False) -> str:
    import avancement  # noqa: PLC0415 - évite la dépendance quand on n'en a pas besoin

    fichiers = sorted(NUITS.glob("*.json")) if NUITS.exists() else []
    nuits = [n for n in (lire_json(f, {}) for f in fichiers) if n and not n.get("rapporte")]
    if not nuits:
        nuits = [{"nuit": (dt.date.today() - dt.timedelta(days=1)).isoformat(), "creneaux": [],
                  "incidents": [{"texte": "aucune équipe de nuit n'a démarré (GitHub n'a pas lancé le travail "
                                          "prévu, ou il ne restait aucune tâche prête)."}]}]
    texte = rapport_nuits(nuits, avancement.texte(avancement.calculer()), lire_json(ETAT / "quota.json", {}))
    if essai:
        print(texte)
        return texte
    if poster(ouvrir(), texte):
        for f in fichiers:
            n = lire_json(f, {})
            if n and not n.get("rapporte"):
                n["rapporte"] = True
                ecrire_json(f, n)
    return texte


def main() -> int:
    parser = argparse.ArgumentParser(description="Bureau de l'organisateur.")
    parser.add_argument("action", choices=["ouvrir", "courrier", "matin"])
    parser.add_argument("--essai", action="store_true")
    args = parser.parse_args()
    if args.action == "ouvrir":
        print(ouvrir())
    elif args.action == "courrier":
        messages = preparer_courrier()
        print(f"{len(messages)} message(s) d'Ange en attente.")
        return 0 if messages else 1
    else:
        matin(args.essai)
    return 0


if __name__ == "__main__":
    sys.exit(main())
