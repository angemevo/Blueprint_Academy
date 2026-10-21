#!/usr/bin/env python3
"""Avancement du projet et date de fin estimée, calculés (pas devinés) à partir de :
  - state/estimation.json : la liste de TOUS les lots du MVP avec leur taille en points,
    tenue par l'organisateur (y compris les lots qui n'ont pas encore d'issue) ;
  - GitHub : une issue fermée = lot terminé, à la date de fermeture.

Le rythme est mesuré sur les 14 derniers jours dès que l'équipe a terminé au moins
3 lots ; avant cela, on utilise la vitesse provisoire de state/estimation.json.

Usage :
  python3 scripts/avancement.py            # texte pour Ange
  python3 scripts/avancement.py --json     # chiffres, pour les rapports
  python3 scripts/avancement.py --hors-ligne   # sans interroger GitHub
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys

from commun import ETAT, gh_json, jour_fr, lire_json

FICHIER = ETAT / "estimation.json"
FENETRE_JOURS = 14
LOTS_MIN_MESURE = 3


def issues_fermees() -> dict[int, dt.date]:
    issues = gh_json("issue", "list", "--state", "closed", "--limit", "300", "--json", "number,closedAt,stateReason")
    return {i["number"]: dt.date.fromisoformat(i["closedAt"][:10]) for i in issues
            if i.get("closedAt") and i.get("stateReason") != "NOT_PLANNED"}


def calculer(aujourdhui: dt.date | None = None, hors_ligne: bool = False) -> dict:
    aujourdhui = aujourdhui or dt.date.today()
    est = lire_json(FICHIER, {})
    lots = est.get("lots") or []
    fermees: dict[int, dt.date] = {}
    source_github = False
    if not hors_ligne:
        try:
            fermees = issues_fermees()
            source_github = True
        except Exception:  # noqa: BLE001 - sans GitHub, on garde les états notés à la main
            pass

    for lot in lots:
        n = lot.get("issue")
        if n in fermees:
            lot["etat"], lot["fait_le"] = "fait", fermees[n].isoformat()

    total = sum(lot.get("points", 0) for lot in lots)
    fait = sum(lot.get("points", 0) for lot in lots if lot.get("etat") == "fait")
    reste = total - fait

    debut = dt.date.fromisoformat(est.get("debut_equipe", aujourdhui.isoformat()))
    depuis = aujourdhui - dt.timedelta(days=FENETRE_JOURS)
    recents = [lot for lot in lots if lot.get("etat") == "fait" and lot.get("fait_le")
               and dt.date.fromisoformat(lot["fait_le"]) >= max(debut, depuis)]
    jours = max(1, min(FENETRE_JOURS, (aujourdhui - debut).days))
    if len(recents) >= LOTS_MIN_MESURE and (aujourdhui - debut).days >= 5:
        vitesse = sum(lot["points"] for lot in recents) / jours
        mesuree = True
    else:
        vitesse = float(est.get("vitesse_provisoire", 2.0))
        mesuree = False
    vitesse = max(vitesse, 0.1)

    def fin(v: float) -> dt.date:
        return aujourdhui + dt.timedelta(days=math.ceil(reste / v))

    attente = [lot for lot in lots if lot.get("etat") != "fait" and lot.get("attend_ange")]
    phases: dict[str, list[int]] = {}
    for lot in lots:
        p = phases.setdefault(str(lot.get("phase", "?")), [0, 0])
        p[1] += lot.get("points", 0)
        if lot.get("etat") == "fait":
            p[0] += lot.get("points", 0)

    return {
        "objectif": est.get("objectif", "MVP"),
        "estimation_maj": est.get("maj"),
        "points_total": total,
        "points_faits": fait,
        "pourcentage": round(100 * fait / total) if total else 0,
        "lots_total": len(lots),
        "lots_faits": sum(lot.get("etat") == "fait" for lot in lots),
        "vitesse_points_jour": round(vitesse, 2),
        "vitesse_mesuree": mesuree,
        "fin_estimee": fin(vitesse).isoformat() if reste else aujourdhui.isoformat(),
        "fin_au_plus_tot": fin(vitesse * 1.3).isoformat() if reste else aujourdhui.isoformat(),
        "fin_au_plus_tard": fin(vitesse * 0.7).isoformat() if reste else aujourdhui.isoformat(),
        "jours_restants": math.ceil(reste / vitesse) if reste else 0,
        "lots_attendant_ange": [lot.get("titre") for lot in attente],
        "phases": {k: {"faits": v[0], "total": v[1]} for k, v in phases.items()},
        "source_github": source_github,
    }


def semaine_de(iso: str) -> str:
    d = dt.date.fromisoformat(iso)
    return jour_fr(d - dt.timedelta(days=d.weekday()), avec_jour=False)


def texte(a: dict) -> str:
    if not a["points_total"]:
        return "Avancement : pas encore d'estimation (state/estimation.json est vide)."
    lignes = [f"**Avancement du {a['objectif']} : {a['pourcentage']} %** "
              f"({a['lots_faits']} lots terminés sur {a['lots_total']}, "
              f"{a['points_faits']} points sur {a['points_total']})."]
    if a["jours_restants"] == 0:
        lignes.append("Tout est livré.")
        return "\n".join(lignes)
    rythme = f"{a['vitesse_points_jour']:g} point(s) par jour"
    rythme += (" (mesuré sur les deux dernières semaines)" if a["vitesse_mesuree"]
               else " (estimation provisoire : le rythme réel sera mesuré dès que l'équipe aura livré 3 lots)")
    lignes.append(f"Rythme de l'équipe : {rythme}.")
    lignes.append(f"**Fin estimée : semaine du {semaine_de(a['fin_estimee'])}** "
                  f"(au plus tôt semaine du {semaine_de(a['fin_au_plus_tot'])}, "
                  f"au plus tard semaine du {semaine_de(a['fin_au_plus_tard'])}).")
    if a["lots_attendant_ange"]:
        lignes.append(f"Cette date suppose que tes validations arrivent à temps pour : "
                      f"{', '.join(a['lots_attendant_ange'])}.")
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Avancement et date de fin estimée.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--hors-ligne", action="store_true")
    args = parser.parse_args()
    a = calculer(hors_ligne=args.hors_ligne)
    print(json.dumps(a, ensure_ascii=False, indent=2) if args.json else texte(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
