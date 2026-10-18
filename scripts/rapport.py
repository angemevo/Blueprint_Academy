#!/usr/bin/env python3
"""Rapport hebdomadaire de l'équipe d'agents, en PDF, pour Ange.

Sources :
  - reports/hebdo/<semaine>.json, écrit par l'orchestrateur au cycle de pilotage (le récit) ;
  - GitHub (PR mergées, issues), state/quota.json, state/livraisons.md (les chiffres) ;
  - les captures et vidéos de qa (branche livrables, ou logs/captures/ en local).

Usage :
  python3 scripts/rapport.py --semaine 2026-S43             # écrit logs/rapports/2026-S43.pdf
  python3 scripts/rapport.py --semaine 2026-S43 --publier   # + release GitHub + issue « Point hebdo »
  python3 scripts/rapport.py --semaine 2026-S43 --donnees essai.json   # sans GitHub (test)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RACINE = Path(__file__).resolve().parent.parent
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre", "décembre"]

# Couleurs : sobres, lisibles à l'impression comme sur téléphone
ENCRE = colors.HexColor("#1d2330")
DOUX = colors.HexColor("#5b6475")
FILET = colors.HexColor("#dfe3ea")
FOND = colors.HexColor("#f4f6f9")
ACCENT = colors.HexColor("#3d5afe")
METEO = {"vert": ("#1f9d55", "Tout avance comme prévu"),
         "orange": ("#d97706", "Avance, avec un point d'attention"),
         "rouge": ("#dc2626", "Bloqué : ton aide est nécessaire")}


# ---------------------------------------------------------------------------
# Polices
# ---------------------------------------------------------------------------
def polices() -> tuple[str, str]:
    for dossier in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"):
        normal, gras = Path(dossier, "DejaVuSans.ttf"), Path(dossier, "DejaVuSans-Bold.ttf")
        if normal.exists() and gras.exists():
            pdfmetrics.registerFont(TTFont("Texte", str(normal)))
            pdfmetrics.registerFont(TTFont("Texte-Gras", str(gras)))
            return "Texte", "Texte-Gras"
    return "Helvetica", "Helvetica-Bold"


TEXTE, GRAS = polices()
S = {
    "titre": ParagraphStyle("titre", fontName=GRAS, fontSize=20, leading=24, textColor=colors.white),
    "soustitre": ParagraphStyle("soustitre", fontName=TEXTE, fontSize=10.5, leading=14,
                                textColor=colors.HexColor("#c9d1ff")),
    "h2": ParagraphStyle("h2", fontName=GRAS, fontSize=13.5, leading=17, textColor=ENCRE,
                         spaceBefore=12, spaceAfter=6),
    "h3": ParagraphStyle("h3", fontName=GRAS, fontSize=11, leading=14, textColor=ENCRE, spaceAfter=2),
    "p": ParagraphStyle("p", fontName=TEXTE, fontSize=10, leading=14.5, textColor=ENCRE),
    "doux": ParagraphStyle("doux", fontName=TEXTE, fontSize=8.8, leading=12, textColor=DOUX),
    "puce": ParagraphStyle("puce", fontName=TEXTE, fontSize=10, leading=14.5, textColor=ENCRE,
                           leftIndent=12, bulletIndent=0, spaceAfter=2),
    "chiffre": ParagraphStyle("chiffre", fontName=GRAS, fontSize=20, leading=23, textColor=ENCRE,
                              alignment=TA_CENTER),
    "etiquette": ParagraphStyle("etiquette", fontName=TEXTE, fontSize=8.5, leading=11, textColor=DOUX,
                                alignment=TA_CENTER),
    "legende": ParagraphStyle("legende", fontName=TEXTE, fontSize=8.5, leading=11.5, textColor=DOUX),
}


def P(texte: str, style: str = "p") -> Paragraph:
    return Paragraph(escape(str(texte)).replace("\n", "<br/>"), S[style])


# ---------------------------------------------------------------------------
# Données
# ---------------------------------------------------------------------------
def bornes(semaine: str) -> tuple[dt.date, dt.date]:
    annee, num = semaine.split("-S")
    lundi = dt.date.fromisocalendar(int(annee), int(num), 1)
    return lundi, lundi + dt.timedelta(days=6)


def periode(semaine: str) -> str:
    debut, fin = bornes(semaine)
    if debut.month == fin.month:
        return f"du {debut.day} au {fin.day} {MOIS[fin.month - 1]} {fin.year}"
    return f"du {debut.day} {MOIS[debut.month - 1]} au {fin.day} {MOIS[fin.month - 1]} {fin.year}"


def gh(*args: str):
    p = subprocess.run(["gh", *args], cwd=RACINE, capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip())
    return json.loads(p.stdout or "null")


def donnees_github(semaine: str) -> dict:
    debut, fin = bornes(semaine)
    merges = gh("pr", "list", "--state", "merged", "--limit", "60",
                "--json", "number,title,mergedAt,url")
    merges = [m for m in merges if debut <= dt.date.fromisoformat(m["mergedAt"][:10]) <= fin]
    ouvertes = gh("pr", "list", "--state", "open", "--limit", "30", "--json", "number,title,url,labels,isDraft")
    issues = gh("issue", "list", "--state", "all", "--limit", "200", "--json", "number,state,labels,closedAt")
    issues = [i for i in issues if not any(e["name"] == "point-hebdo" for e in i["labels"])]
    fermees_semaine = [i for i in issues if i["state"] == "CLOSED" and i.get("closedAt")
                       and debut <= dt.date.fromisoformat(i["closedAt"][:10]) <= fin]
    return {
        "merges": merges,
        "pr_ouvertes": ouvertes,
        "issues_ouvertes": sum(i["state"] == "OPEN" for i in issues),
        "issues_fermees": sum(i["state"] == "CLOSED" for i in issues),
        "issues_fermees_semaine": len(fermees_semaine),
        "depot": gh("repo", "view", "--json", "nameWithOwner")["nameWithOwner"],
    }


def quota() -> dict:
    try:
        return json.loads((RACINE / "state" / "quota.json").read_text())
    except (OSError, ValueError):
        return {}


def cycles_semaine(semaine: str) -> tuple[int, int]:
    debut, fin = bornes(semaine)
    faits = coupes = 0
    try:
        for ligne in (RACINE / "state" / "quota.md").read_text(encoding="utf-8").splitlines():
            morceaux = [m.strip() for m in ligne.strip("|").split("|")]
            try:
                jour = dt.date.fromisoformat(morceaux[0])
            except (ValueError, IndexError):
                continue
            if debut <= jour <= fin:
                faits += 1
                coupes += "coupé" in ligne
    except OSError:
        pass
    return faits, coupes


def dossier_captures() -> list[Path]:
    """Où chercher captures/pr-<n>/ : la branche livrables (extraite), puis logs/captures."""
    dossiers = [RACINE / "logs" / "captures"]
    try:
        subprocess.run(["git", "fetch", "-q", "origin", "livrables"], cwd=RACINE, check=True,
                       capture_output=True, timeout=120)
        cible = Path(tempfile.mkdtemp(prefix="livrables-"))
        archive = subprocess.run(["git", "archive", "origin/livrables", "captures"], cwd=RACINE,
                                 capture_output=True, check=True, timeout=120)
        subprocess.run(["tar", "-x", "-C", str(cible)], input=archive.stdout, check=True)
        dossiers.insert(0, cible / "captures")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return dossiers


def captures_de(pr: int | None, dossiers: list[Path]) -> tuple[list[tuple[Path, str]], bool]:
    if not pr:
        return [], False
    for base in dossiers:
        d = base / f"pr-{pr}"
        if (d / "resultat.json").exists():
            r = json.loads((d / "resultat.json").read_text(encoding="utf-8"))
            images = [(d / c["fichier"], c["legende"]) for c in r.get("captures", []) if (d / c["fichier"]).exists()]
            return images, bool(r.get("video"))
    return [], False


# ---------------------------------------------------------------------------
# Mise en page
# ---------------------------------------------------------------------------
def bandeau(semaine: str, recit: dict) -> Table:
    t = Table([[P("Blueprint Academy · point hebdo", "titre")],
               [P(f"Semaine {semaine.split('-S')[1]} · {periode(semaine)} · rapport de l'équipe d'agents",
                  "soustitre")]],
              colWidths=[180 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), ENCRE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                           ("TOPPADDING", (0, 0), (-1, 0), 14), ("BOTTOMPADDING", (0, -1), (-1, -1), 14)]))
    return t


def meteo(recit: dict) -> Table:
    couleur, libelle = METEO.get(recit.get("meteo", "vert"), METEO["vert"])
    pastille = Table([[""]], colWidths=[5 * mm], rowHeights=[5 * mm])
    pastille.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(couleur)),
                                  ("ROUNDEDCORNERS", [2.5, 2.5, 2.5, 2.5])]))
    t = Table([[pastille, Paragraph(f"<b>Météo du projet :</b> {escape(libelle)}", S["p"])]],
              colWidths=[9 * mm, 171 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def tuiles(chiffres: list[tuple[str, str]]) -> Table:
    cellules = [[P(v, "chiffre"), ] for v, _ in chiffres]
    ligne_v = [c[0] for c in cellules]
    ligne_e = [P(e, "etiquette") for _, e in chiffres]
    largeur = 180 * mm / len(chiffres)
    t = Table([ligne_v, ligne_e], colWidths=[largeur] * len(chiffres))
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FOND),
                           ("LINEAFTER", (0, 0), (-2, -1), 3, colors.white),
                           ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, -1), (-1, -1), 10)]))
    return t


def barre(fait: int, total: int) -> Table:
    part = fait / total if total else 0
    largeur = 180 * mm
    plein = max(part * largeur, 0.1)
    t = Table([["", ""]], colWidths=[plein, max(largeur - plein, 0.1)], rowHeights=[3.2 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), ACCENT), ("BACKGROUND", (1, 0), (1, 0), FILET),
                           ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def image(chemin: Path, largeur: float) -> Image:
    larg, haut = ImageReader(str(chemin)).getSize()
    hauteur = largeur * haut / larg
    if hauteur > 120 * mm:  # page entière : on la réduit
        largeur, hauteur = largeur * 120 * mm / hauteur, 120 * mm
    img = Image(str(chemin), width=largeur, height=hauteur)
    img.hAlign = "LEFT"
    return img


def puces(elements: list[str]) -> list[Paragraph]:
    return [Paragraph(escape(str(e)), S["puce"], bulletText="•") for e in elements]


def construire(semaine: str, recit: dict, auto: dict, sortie: Path) -> None:
    q = quota()
    sept = q.get("seven_day", {}).get("utilization")
    cycles, coupes = cycles_semaine(semaine)
    total = auto["issues_ouvertes"] + auto["issues_fermees"]
    dossiers = dossier_captures()
    depot = auto.get("depot", "angemevo/Blueprint_Academy")

    h = [bandeau(semaine, recit), Spacer(1, 10), meteo(recit), Spacer(1, 8)]
    if recit.get("en_bref"):
        h += [P("En bref", "h2"), *puces(recit["en_bref"])]
    h += [Spacer(1, 8), tuiles([
        (str(len(auto["merges"])), "livraisons cette semaine"),
        (str(len(auto["pr_ouvertes"])), "en cours de revue"),
        (str(auto["issues_ouvertes"]), "tâches restantes"),
        (f"{round(sept * 100)} %" if sept is not None else "–", "du quota Claude de la semaine"),
    ]), Spacer(1, 8)]
    if total:
        h += [P(f"Avancement des tâches prévues : {auto['issues_fermees']} terminées sur {total}", "doux"),
              Spacer(1, 3), barre(auto["issues_fermees"], total)]
    h.append(P(f"{cycles} cycle(s) de travail cette semaine" + (f", dont {coupes} interrompu(s) par la limite d'usage."
                                                               if coupes else "."), "doux"))

    # Livré
    h.append(P("Ce qui a été livré", "h2"))
    livres = recit.get("livre") or [{"titre": m["title"], "pr": m["number"]} for m in auto["merges"]]
    if not livres:
        h.append(P("Rien n'a été livré cette semaine.", "p"))
    for item in livres:
        bloc = [P(item.get("titre", ""), "h3")]
        if item.get("pour_l_utilisateur"):
            bloc.append(P(item["pour_l_utilisateur"]))
        images, video = captures_de(item.get("pr"), dossiers)
        for chemin, legende in images[:3]:
            bloc += [Spacer(1, 4), image(chemin, 150 * mm), P(legende, "legende")]
        refs = []
        if item.get("pr"):
            refs.append(f'<a href="https://github.com/{depot}/pull/{item["pr"]}" color="#3d5afe">PR #{item["pr"]}</a>')
        if video:
            refs.append(f'<a href="https://github.com/{depot}/blob/livrables/captures/pr-{item["pr"]}/video.webm" '
                        'color="#3d5afe">voir la vidéo de démonstration</a>')
        if refs:
            bloc.append(Paragraph(" · ".join(refs), S["doux"]))
        h += [KeepTogether(bloc[:2]), *bloc[2:], Spacer(1, 8)]

    if recit.get("en_cours"):
        h.append(P("En cours", "h2"))
        h += puces([f"{e.get('titre', '')} : {e.get('etat', '')}" if isinstance(e, dict) else e
                    for e in recit["en_cours"]])
    if recit.get("semaine_prochaine"):
        h.append(P("La semaine prochaine", "h2"))
        h += puces(recit["semaine_prochaine"])
    if recit.get("decisions_prises"):
        h.append(P("Décisions prises par l'équipe", "h2"))
        h += puces([f"{d.get('decision', '')} ({d.get('pourquoi', '')})" if isinstance(d, dict) else d
                    for d in recit["decisions_prises"]])
    if recit.get("risques"):
        h.append(P("Risques", "h2"))
        h += puces([f"{r.get('risque', '')} — ce qu'on fait : {r.get('ce_qu_on_fait', '')}"
                    if isinstance(r, dict) else r for r in recit["risques"]])

    # Questions pour Ange
    questions = list(recit.get("questions") or [])
    for pr in auto["pr_ouvertes"]:
        if any(e["name"] == "a-valider-ange" for e in pr.get("labels", [])):
            questions.append({"id": f"PR{pr['number']}",
                              "question": f"Valider la PR #{pr['number']} « {pr['title']} » ?",
                              "contexte": "Elle touche des fichiers sensibles ou elle est grande : "
                                          "le portier ne la merge pas seul.",
                              "options": ["Oui : merge-la", "Non : explique pourquoi en commentaire"],
                              "recommandation": "Voir la revue de qa sur la PR."})
    h.append(P("Tes décisions", "h2"))
    if not questions:
        h.append(P("Aucune décision n'est attendue de toi cette semaine.", "p"))
    else:
        h.append(P("Réponds en commentaire de l'issue « Point hebdo » de cette semaine, par exemple "
                   "« Q1 : A ». Sans réponse à la date indiquée, l'équipe applique sa recommandation.", "doux"))
        for qn in questions:
            bloc = [P(f"{qn.get('id', '?')} · {qn.get('question', '')}", "h3")]
            if qn.get("contexte"):
                bloc.append(P(qn["contexte"]))
            bloc += puces(qn.get("options", []))
            reco = qn.get("recommandation")
            if reco:
                fin = f" Appliquée le {qn['sans_reponse_le']} sans réponse." if qn.get("sans_reponse_le") else ""
                bloc.append(P(f"Recommandation de l'équipe : {reco}.{fin}".replace("..", "."), "doux"))
            h += [KeepTogether(bloc), Spacer(1, 6)]

    if auto["merges"]:
        h.append(P("Annexe : PR mergées", "h2"))
        lignes = [[P("PR", "doux"), P("Titre", "doux"), P("Date", "doux")]]
        for m in auto["merges"]:
            lignes.append([P(f"#{m['number']}"), P(m["title"]), P(m["mergedAt"][:10])])
        t = Table(lignes, colWidths=[16 * mm, 134 * mm, 30 * mm], repeatRows=1)
        t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.4, FILET), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        h.append(t)

    def pied(canvas, doc):
        canvas.saveState()
        canvas.setFont(TEXTE, 7.5)
        canvas.setFillColor(DOUX)
        canvas.drawString(15 * mm, 10 * mm, f"Généré automatiquement le {dt.date.today().strftime('%d/%m/%Y')} "
                                            "par l'équipe d'agents")
        canvas.drawRightString(195 * mm, 10 * mm, f"page {doc.page}")
        canvas.restoreState()

    sortie.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(sortie), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=14 * mm, bottomMargin=16 * mm,
                            title=f"Blueprint Academy — point hebdo {semaine}", author="Équipe d'agents")
    doc.build(h, onFirstPage=pied, onLaterPages=pied)


# ---------------------------------------------------------------------------
# Publication : release GitHub (le PDF) et issue « Point hebdo » (les questions)
# ---------------------------------------------------------------------------
def publier(semaine: str, recit: dict, auto: dict, pdf: Path) -> None:
    depot, tag = auto["depot"], f"rapport-{semaine}"
    notes = "\n".join(f"- {e}" for e in recit.get("en_bref", [])) or "Rapport hebdomadaire de l'équipe d'agents."
    existe = subprocess.run(["gh", "release", "view", tag], cwd=RACINE, capture_output=True).returncode == 0
    if existe:
        subprocess.run(["gh", "release", "upload", tag, str(pdf), "--clobber"], cwd=RACINE, check=True)
    else:
        subprocess.run(["gh", "release", "create", tag, str(pdf), "--title", f"Point hebdo {semaine}",
                        "--notes", notes, "--latest=false"], cwd=RACINE, check=True)
    lien = f"https://github.com/{depot}/releases/download/{tag}/{pdf.name}"

    subprocess.run(["gh", "label", "create", "point-hebdo", "--color", "3D5AFE", "--force",
                    "--description", "Point hebdomadaire de l'équipe d'agents pour Ange"], cwd=RACINE,
                   capture_output=True)
    couleur, libelle = METEO.get(recit.get("meteo", "vert"), METEO["vert"])
    corps = [f"**Météo : {libelle}**", "", f"📄 **[Lire le rapport PDF]({lien})**", ""]
    if recit.get("en_bref"):
        corps += ["## En bref", *[f"- {e}" for e in recit["en_bref"]], ""]
    questions = recit.get("questions") or []
    corps.append("## Tes décisions")
    if questions:
        corps.append("Réponds en commentaire, par exemple `Q1 : A`. Sans réponse à la date indiquée, "
                     "l'équipe applique sa recommandation.\n")
        for qn in questions:
            corps.append(f"**{qn.get('id')} · {qn.get('question')}**")
            if qn.get("contexte"):
                corps.append(qn["contexte"])
            corps += [f"- {o}" for o in qn.get("options", [])]
            if qn.get("recommandation"):
                date_defaut = qn.get("sans_reponse_le")
                suite = f" (appliquée le {date_defaut} sans réponse)_" if date_defaut else "_"
                corps.append(f"\n_Recommandation : {qn['recommandation']}{suite}")
            corps.append("")
    else:
        corps.append("Aucune décision n'est attendue de toi cette semaine.")
    a_valider = [p for p in auto["pr_ouvertes"] if any(e["name"] == "a-valider-ange" for e in p.get("labels", []))]
    if a_valider:
        corps += ["", "## PR qui attendent ton feu vert"] + [f"- #{p['number']} {p['title']}" for p in a_valider]
    fichier = RACINE / "logs" / f"point-hebdo-{semaine}.md"
    fichier.write_text("\n".join(corps), encoding="utf-8")

    precedentes = gh("issue", "list", "--label", "point-hebdo", "--state", "open", "--json", "number,title")
    titre = f"Point hebdo {semaine} : rapport et décisions"
    meme = [i for i in precedentes if i["title"] == titre]
    if meme:
        subprocess.run(["gh", "issue", "edit", str(meme[0]["number"]), "--body-file", str(fichier)],
                       cwd=RACINE, check=True)
        numero = meme[0]["number"]
    else:
        url = subprocess.run(["gh", "issue", "create", "--title", titre, "--label", "point-hebdo",
                              "--assignee", depot.split("/")[0], "--body-file", str(fichier)],
                             cwd=RACINE, check=True, capture_output=True, text=True).stdout.strip()
        numero = int(url.rstrip("/").split("/")[-1])
    for i in precedentes:
        if i["number"] != numero:
            subprocess.run(["gh", "issue", "close", str(i["number"]), "--comment",
                            f"Remplacé par le point de la semaine suivante : #{numero}."], cwd=RACINE)
    print(f"Rapport publié : {lien} · issue #{numero}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semaine", default=dt.date.today().strftime("%G-S%V"))
    parser.add_argument("--publier", action="store_true")
    parser.add_argument("--donnees", type=Path, help="chiffres GitHub simulés (test hors ligne)")
    parser.add_argument("--sortie", type=Path)
    args = parser.parse_args()

    fichier_recit = RACINE / "reports" / "hebdo" / f"{args.semaine}.json"
    try:
        recit = json.loads(fichier_recit.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"Récit absent ou illisible ({fichier_recit.name} : {e}) : rapport avec les seuls chiffres.",
              file=sys.stderr)
        recit = {"meteo": "orange", "en_bref": ["L'orchestrateur n'a pas écrit le bilan de la semaine : "
                                                 "ce rapport ne contient que les chiffres."]}
    auto = json.loads(args.donnees.read_text()) if args.donnees else donnees_github(args.semaine)
    sortie = args.sortie or RACINE / "logs" / "rapports" / f"{args.semaine}.pdf"
    construire(args.semaine, recit, auto, sortie)
    print(f"PDF : {sortie}")
    if args.publier and not args.donnees:
        publier(args.semaine, recit, auto, sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())
