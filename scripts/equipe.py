#!/usr/bin/env python3
"""Fait travailler l'équipe d'agents, avec l'abonnement Claude Pro d'Ange, sans lui.

Modes :
  nuit      l'équipe de nuit : le chef d'équipe planifie des créneaux, chacun est exécuté dans
            sa propre session (développeur puis qa), le portier livre après chaque créneau.
            Une erreur n'arrête jamais la nuit : le créneau est repris une fois, puis mis de côté,
            et l'équipe passe au suivant. Arrêt seulement à l'heure de fin ou au quota.
  tech      un seul créneau, au choix du chef d'équipe (pour un essai à la main).
  courrier  l'organisateur répond aux messages d'Ange dans son bureau (issue « bureau »).
  matin     le rapport de la nuit est publié dans le bureau (sans Claude).
  pilotage  le dimanche : bilan, plan de la semaine, estimation, rapport PDF.
  rapport   régénère seulement le PDF de la semaine (sans Claude).

Variables (toutes facultatives) : NTFY_TOPIC, QUOTA_MAX_SEMAINE (0.70), QUOTA_MAX_5H (0.92),
DUREE_EQUIPE_MIN (320), CRENEAUX_MAX (8), FIN_NUIT (07:30, heure UTC où une équipe programmée
s'arrête, pour laisser à Ange sa journée et son quota ; ne s'applique pas à un lancement à la main).
Appelé par scripts/cycle.sh (GitHub Actions ou cron d'un ordinateur).
"""
from __future__ import annotations

import datetime as dt
import fcntl
import functools
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import bureau
from commun import ETAT, LOGS, RACINE, cle_nuit, ecrire_json, heure_fr, lancer, lire_json, maintenant, notifier

EN_CLOUD = bool(os.environ.get("GITHUB_ACTIONS"))
QUOTA_MAX_SEMAINE = float(os.environ.get("QUOTA_MAX_SEMAINE") or 0.70)
QUOTA_MAX_5H = float(os.environ.get("QUOTA_MAX_5H") or 0.92)
DUREE_EQUIPE_MIN = int(os.environ.get("DUREE_EQUIPE_MIN") or 320)
CRENEAUX_MAX = int(os.environ.get("CRENEAUX_MAX") or 8)
FIN_NUIT = os.environ.get("FIN_NUIT") or "07:30"
DEBUT_NUIT = "19:30"
TYPES_CRENEAU = {"dev", "reprise", "revue"}
CIBLE = re.compile(r"^(issue|pr)\s*#?\s*(\d+)$", re.IGNORECASE)
STACK = ["docker", "compose", "up", "-d", "--wait", "postgres", "backend", "frontend"]
BRANCHE = "master"
DEBUT = time.monotonic()
MINUTE = 60  # secondes ; les tests de simulation la raccourcissent


def journal(msg: str) -> None:
    print(f"[{heure_fr(maintenant())}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Git : point de départ propre, sauvegarde de l'état après chaque étape
# ---------------------------------------------------------------------------
def code_modifie() -> bool:
    ok, sortie = lancer(["git", "status", "--porcelain", "--", ".", ":!state", ":!reports", ":!logs",
                         ":!frontend/next-env.d.ts"])
    return ok and bool(sortie.strip())


def revenir_sur_master(contexte: str) -> str | None:
    """Range le travail non commité d'un agent et revient sur master. Renvoie un incident éventuel."""
    incident = None
    lancer(["git", "restore", "--", "frontend/next-env.d.ts"])
    if lancer(["git", "rebase", "--show-current-patch"])[0] or (RACINE / ".git" / "rebase-merge").exists():
        lancer(["git", "rebase", "--abort"])
    if (RACINE / ".git" / "MERGE_HEAD").exists():
        lancer(["git", "merge", "--abort"])
    if code_modifie():
        lancer(["git", "stash", "push", "-u", "-m", f"{contexte} {maintenant().isoformat()}", "--",
                ".", ":!state", ":!reports", ":!logs"])
        incident = f"{contexte} : du travail non enregistré a été mis de côté (le prochain essai repart de la branche)."
    ok, _ = lancer(["git", "switch", "-q", BRANCHE])
    if not ok:
        lancer(["git", "switch", "-q", "-f", BRANCHE])
    return incident


def mettre_a_jour() -> bool:
    for _ in range(3):
        if lancer(["git", "pull", "-q", "--rebase", "--autostash", "origin", BRANCHE], timeout=120)[0]:
            return True
        lancer(["git", "rebase", "--abort"])
        time.sleep(5)
    return False


def sauver_etat(message: str) -> None:
    """Committe state/ et reports/ sur master et pousse, pour ne rien perdre si la machine s'arrête."""
    lancer(["git", "add", "state", "reports"])
    if lancer(["git", "diff", "--cached", "--quiet"])[0]:
        return
    lancer(["git", "commit", "-q", "-m", message])
    for essai in range(4):
        if not lancer(["git", "pull", "-q", "--rebase", "--autostash", "origin", BRANCHE], timeout=120)[0]:
            lancer(["git", "rebase", "--abort"])
            # Dernier recours : fusion où notre état l'emporte (fichiers state/ seulement)
            lancer(["git", "pull", "-q", "--no-rebase", "-X", "ours", "origin", BRANCHE], timeout=120)
        if lancer(["git", "push", "-q", "origin", BRANCHE], timeout=120)[0]:
            return
        time.sleep(5 * (essai + 1))
    notifier("Équipe d'agents", "L'état de l'équipe n'a pas pu être enregistré sur GitHub (push refusé).")


def publier_livrables() -> None:
    lancer(["bash", "scripts/publier-livrables.sh"], timeout=300)


# ---------------------------------------------------------------------------
# Claude : une session headless = un journal .jsonl (rejouable dans la salle de réunion)
# ---------------------------------------------------------------------------
def approuver_dossier() -> bool:
    """En mode -p, Claude Code n'applique les réglages du dépôt que si le dossier est approuvé."""
    conf_path = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home()) / ".claude.json"
    conf = lire_json(conf_path, {})
    projet = conf.setdefault("projects", {}).setdefault(str(RACINE), {})
    if EN_CLOUD:
        conf["hasCompletedOnboarding"] = True
        projet["hasTrustDialogAccepted"] = True
        conf_path.write_text(json.dumps(conf), encoding="utf-8")
        return True
    return bool(projet.get("hasTrustDialogAccepted"))


@functools.lru_cache(maxsize=1)
def options_flux() -> tuple[str, ...]:
    opts = ["--output-format", "stream-json", "--verbose"]
    ok, aide = lancer(["claude", "--help"], timeout=60)
    if ok and "--forward-subagent-text" in aide:
        opts.append("--forward-subagent-text")
    return tuple(opts)


class Session:
    """Résultat d'une session : code, texte final, coupure par le quota."""

    def __init__(self, code: int, resultat: str, quota_coupe: bool, delai: bool, journal_: Path, minutes: int):
        self.code, self.resultat, self.quota_coupe, self.delai = code, resultat, quota_coupe, delai
        self.journal, self.minutes = journal_, minutes

    @property
    def reussie(self) -> bool:
        return self.code == 0 and not self.delai and not self.quota_coupe


def session_claude(invite: str, nom: str, minutes_max: int) -> Session:
    LOGS.mkdir(exist_ok=True)
    debut = maintenant()
    log = LOGS / f"{debut.strftime('%Y-%m-%d_%H%M')}-{nom}.jsonl"
    err = log.with_suffix(".err")
    with log.open("w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "cycle_start", "cycle": nom, "started_at": debut.isoformat()}) + "\n")
    if not lancer(["which", "claude"])[0]:
        return Session(127, "claude introuvable", False, False, log, 0)
    cmd = ["claude", "-p", invite, "--permission-mode", "acceptEdits", "--permission-prompts", "none",
           *options_flux()]
    delai = False
    with log.open("a", encoding="utf-8") as sortie, err.open("w", encoding="utf-8") as erreurs:
        proc = subprocess.Popen(cmd, cwd=RACINE, stdout=sortie, stderr=erreurs, start_new_session=True)
        try:
            code = proc.wait(timeout=minutes_max * MINUTE)
        except subprocess.TimeoutExpired:
            delai = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                code = proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait()
    fin = maintenant()
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"type": "cycle_end", "cycle": nom, "exit_code": code, "ended_at": fin.isoformat()}) + "\n")

    resultat, refuse = "", False
    for ligne in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if '"type":"result"' in ligne.replace(" ", ""):
            try:
                resultat = json.loads(ligne).get("result") or resultat
            except ValueError:
                pass
        elif '"rate_limit_event"' in ligne:
            try:
                info = json.loads(ligne)["rate_limit_info"]
                refuse = refuse or info.get("status") not in (None, "allowed", "allowed_warning")
                maj_quota(info)
            except (ValueError, KeyError):
                pass
    texte_err = err.read_text(encoding="utf-8", errors="replace")[-2000:] if err.exists() else ""
    if code != 0 and re.search(r"usage limit|rate limit|limit reached|5-hour limit|weekly limit", texte_err + resultat, re.I):
        refuse = True
    if code != 0 and re.search(r"OAuth token|401|invalid api key|authentication", texte_err, re.I):
        notifier("Équipe d'agents", "La clé Claude de GitHub ne marche plus : refais « claude setup-token » "
                                    "et remplace le secret CLAUDE_CODE_OAUTH_TOKEN (docs/equipe-cloud.md).")
    return Session(code, resultat, refuse, delai, log, max(1, int((fin - debut).total_seconds() // 60)))


# ---------------------------------------------------------------------------
# Quota Claude : le dernier état connu décide si l'équipe continue, attend ou s'arrête
# ---------------------------------------------------------------------------
def maj_quota(info: dict) -> None:
    fenetres = info.get("unifiedWindows")
    if not fenetres:
        return
    q = dict(fenetres)
    q["status"] = info.get("status")
    q["maj"] = maintenant().isoformat()
    ecrire_json(ETAT / "quota.json", q)


def decision_quota(fin_equipe: float) -> tuple[str, int]:
    """('ok', 0), ('attendre', secondes) ou ('stop', 0)."""
    q = lire_json(ETAT / "quota.json", {})
    maintenant_s = time.time()
    sept = q.get("seven_day") or {}
    if sept.get("resetsAt", 0) > maintenant_s and sept.get("utilization", 0) >= QUOTA_MAX_SEMAINE:
        return "stop", 0
    cinq = q.get("five_hour") or {}
    if cinq.get("resetsAt", 0) > maintenant_s and cinq.get("utilization", 0) >= QUOTA_MAX_5H:
        attente = int(cinq["resetsAt"] - maintenant_s) + 120
        reste = fin_equipe - time.monotonic()
        return ("attendre", attente) if attente < reste - 30 * MINUTE else ("stop", 0)
    return "ok", 0


# ---------------------------------------------------------------------------
# Préparation commune
# ---------------------------------------------------------------------------
def verrou():
    f = open(f"/tmp/agents-{RACINE.name}.lock", "w")  # noqa: SIM115 - gardé ouvert jusqu'à la fin
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        journal("Une équipe travaille déjà sur ce dépôt : abandon.")
        sys.exit(0)
    return f


def preparer(mode: str) -> None:
    besoin = ["gh", "git"] + (["claude"] if mode in ("nuit", "tech", "courrier", "pilotage") else [])
    besoin += ["docker"] if mode in ("nuit", "tech") else []
    for outil in besoin:
        if not lancer(["which", outil])[0]:
            notifier("Équipe d'agents", f"Travail annulé : l'outil {outil} est introuvable.")
            sys.exit(1)
    if code_modifie() and not EN_CLOUD:
        notifier("Équipe d'agents", "Travail annulé : le dépôt contient des modifications non enregistrées.")
        sys.exit(1)
    revenir_sur_master("Démarrage")
    if not mettre_a_jour():
        notifier("Équipe d'agents", f"Travail annulé : impossible de mettre {BRANCHE} à jour.")
        sys.exit(1)
    if "claude" in besoin and not approuver_dossier():
        notifier("Équipe d'agents", f"Travail annulé : lance « claude » une fois dans {RACINE} et accepte le dossier.")
        sys.exit(3)


def stack_prete() -> bool:
    if not (RACINE / ".env").exists() and (RACINE / ".env.example").exists() and EN_CLOUD:
        (RACINE / ".env").write_text((RACINE / ".env.example").read_text())
    for cmd in (STACK, ["docker", "compose", "restart"], STACK + ["--build"]):
        ok, sortie = lancer(cmd, timeout=900)
        if ok and cmd != ["docker", "compose", "restart"]:
            return True
        (LOGS / "docker.log").write_text(sortie[-5000:], encoding="utf-8")
    return False


# ---------------------------------------------------------------------------
# La nuit
# ---------------------------------------------------------------------------
class Nuit:
    def __init__(self) -> None:
        self.cle = cle_nuit()
        self.chemin = ETAT / "nuits" / f"{self.cle}.json"
        self.d = lire_json(self.chemin, {}) or {"nuit": self.cle, "equipes": [], "creneaux": [], "merges": [],
                                              "incidents": [], "rapporte": False}
        self.d["rapporte"] = False
        self.d["equipes"].append({"debut": maintenant().isoformat(), "run": os.environ.get("GITHUB_RUN_ID", "local")})

    def sauver(self) -> None:
        ecrire_json(self.chemin, self.d)

    def incident(self, texte: str) -> None:
        journal(f"Incident : {texte}")
        self.d["incidents"].append({"quand": maintenant().isoformat(), "texte": f"{heure_fr(maintenant())} — {texte}"})
        self.sauver()

    def a_faire(self) -> list[dict]:
        return [c for c in self.d["creneaux"] if c["statut"] == "a_faire"]

    def terminer(self, raison: str) -> None:
        self.d["equipes"][-1].update({"fin": maintenant().isoformat(), "raison_fin": raison})
        self.sauver()


def empreinte_consignes() -> str:
    h = hashlib.sha256()
    for nom in ("consignes.md", "cycle-courant.md", "validations.md"):
        try:
            h.update((ETAT / nom).read_bytes())
        except OSError:
            pass
    return h.hexdigest()


def planifier(nuit: Nuit, minutes_restantes: int) -> bool:
    """Le chef d'équipe distribue les créneaux. Renvoie False s'il n'y a rien à faire."""
    brouillon = LOGS / "planning.json"
    brouillon.unlink(missing_ok=True)
    historique = [f"{c['type']} {c['cible']} : {c['statut']}" for c in nuit.d["creneaux"]]
    invite = (f"/planifier-nuit {minutes_restantes} minutes disponibles, {CRENEAUX_MAX} créneaux au plus. "
              f"Déjà fait cette nuit : {'; '.join(historique) or 'rien'}.")
    s = session_claude(invite, "chef-planning", 25)
    plan = lire_json(brouillon, None)
    creneaux = []
    if isinstance(plan, dict):
        for brut in (plan.get("creneaux") or [])[:CRENEAUX_MAX]:
            m = CIBLE.match(str(brut.get("cible", "")).strip())
            if brut.get("type") not in TYPES_CRENEAU or not m:
                continue
            creneaux.append({
                "n": len(nuit.d["creneaux"]) + len(creneaux) + 1, "type": brut["type"],
                "cible": f"{m.group(1).lower()} {m.group(2)}", "titre": str(brut.get("titre", ""))[:120],
                "minutes": max(10, min(120, int(brut.get("minutes") or 45))),
                "pourquoi": str(brut.get("pourquoi", ""))[:300], "statut": "a_faire", "tentatives": 0,
            })
    if not creneaux and isinstance(plan, dict) and plan.get("rien_a_faire"):
        nuit.incident(f"Le chef d'équipe n'a plus de tâche prête : {str(plan['rien_a_faire'])[:300]}")
        return False
    if not creneaux:
        # Planning illisible ou session ratée : le chef choisira lui-même à chaque créneau
        nuit.incident("le planning du chef d'équipe était illisible"
                      f"{' (session interrompue)' if not s.reussie else ''} : l'équipe continue avec un créneau "
                      "au choix du chef.")
        creneaux = [{"n": len(nuit.d["creneaux"]) + 1, "type": "auto", "cible": "auto", "titre": "tâche prioritaire",
                     "minutes": 60, "pourquoi": "planning de secours", "statut": "a_faire", "tentatives": 0}]
    nuit.d["creneaux"].extend(creneaux)
    nuit.d["empreinte_consignes"] = empreinte_consignes()
    nuit.sauver()
    journal("Planning : " + " | ".join(f"{c['n']}. {c['type']} {c['cible']} ({c['minutes']} min)" for c in creneaux))
    return True


def nouvel_essai(nuit: Nuit, c: dict, **changements) -> dict:
    """Copie propre d'un créneau à refaire, placée en fin de planning."""
    garde = {k: v for k, v in c.items() if k not in ("debut", "minutes_reelles", "journal", "resume")}
    garde.update({"n": len(nuit.d["creneaux"]) + 1, "statut": "a_faire", **changements})
    nuit.d["creneaux"].append(garde)
    return garde


def invite_creneau(c: dict) -> str:
    if c["type"] == "auto":
        return "/creneau auto"
    texte = (f"/creneau Créneau {c['n']} : {c['type']} sur {c['cible']} ({c.get('titre', '')}). "
             f"Durée : {c['minutes']} minutes.")
    if c.get("suites"):
        texte += " Suite d'un créneau précédent qui a commencé ce travail : reprends la branche ou la PR existante."
    if c["tentatives"]:
        texte += f" Tentative {c['tentatives'] + 1} : la précédente s'est arrêtée ({c.get('dernier_probleme', '')})."
    return texte


def lire_resume(texte: str) -> tuple[str, str]:
    """Le chef termine chaque créneau par « STATUT : … » et « RÉSUMÉ : … »."""
    statut = re.search(r"STATUT\s*:\s*\**\s*(fait|bloqu|partiel)", texte or "", re.I)
    resume = re.search(r"R[ÉE]SUM[ÉE]\s*:\s*(.+)", texte or "", re.I | re.S)
    s = (statut.group(1).lower() if statut else "fait")
    return ("bloque" if s.startswith("bloqu") else "partiel" if s == "partiel" else "fait",
            (resume.group(1) if resume else (texte or "")).strip()[:600])


def executer_creneau(nuit: Nuit, c: dict, fin_equipe: float) -> None:
    reste_min = int((fin_equipe - time.monotonic()) / MINUTE)
    limite = max(10, min(int(c["minutes"] * 1.5), 120, reste_min))
    c.update({"statut": "en_cours", "debut": maintenant().isoformat()})
    nuit.sauver()
    nom = f"creneau-{c['n']}-{c['type']}-{c['cible'].replace(' ', '')}"
    journal(f"Créneau {c['n']} : {c['type']} {c['cible']} ({limite} min au plus)")
    s = session_claude(invite_creneau(c), nom, limite)
    c["minutes_reelles"] = c.get("minutes_reelles", 0) + s.minutes
    c["journal"] = s.journal.name
    c["tentatives"] += 1
    rangement = revenir_sur_master(f"Créneau {c['n']}")
    if rangement:
        nuit.incident(rangement)

    if s.reussie:
        statut, resume = lire_resume(s.resultat)
        c["resume"] = resume
        c["statut"] = "bloque" if statut == "bloque" else "fait"
        if statut == "bloque":
            nuit.incident(f"Créneau {c['n']} ({c['cible']}) bloqué : {resume[:250]} L'équipe passe à la suite ; "
                          "le blocage est dans le plan pour l'organisateur.")
        elif statut == "partiel" and c.get("suites", 0) < 2:
            # Travail commencé, branche poussée : un créneau de plus pour le terminer
            nouvel_essai(nuit, c, tentatives=0, suites=c.get("suites", 0) + 1,
                         dernier_probleme="travail commencé, à terminer")
        nuit.sauver()
        return

    probleme = ("quota Claude atteint" if s.quota_coupe else
                f"temps dépassé ({limite} min)" if s.delai else f"erreur de la session (code {s.code})")
    c["dernier_probleme"] = probleme
    if s.quota_coupe:
        c["statut"] = "quota"
        nuit.incident(f"Créneau {c['n']} ({c['cible']}) interrompu : {probleme}. Il sera repris dès que possible.")
        nouvel_essai(nuit, c, tentatives=c["tentatives"] - 1)
    elif c["tentatives"] < 2:
        c["statut"] = "echec"
        nuit.incident(f"Créneau {c['n']} ({c['cible']}) : {probleme}. Le chef d'équipe le relance une fois.")
        nouvel_essai(nuit, c)
    else:
        c["statut"] = "bloque"
        nuit.incident(f"Créneau {c['n']} ({c['cible']}) : {probleme}, deuxième fois. Tâche mise de côté pour "
                      "l'organisateur ; l'équipe passe à la suivante.")
    nuit.sauver()


def portier(nuit: Nuit | None) -> str:
    try:
        p = subprocess.run([sys.executable, "scripts/portier.py"], cwd=RACINE, capture_output=True, text=True,
                           timeout=3600)
        ok, bilan = p.returncode == 0, p.stdout.strip()  # stdout = le bilan ; stderr = le détail des tests
        (LOGS / "portier.log").open("a", encoding="utf-8").write(p.stderr)
    except subprocess.TimeoutExpired:
        ok, bilan = False, "délai dépassé"
    revenir_sur_master("Portier")
    mettre_a_jour()
    if nuit is not None:
        for phrase in re.findall(r"PR #\d+ mergée : .+?\.(?= PR #|$)", bilan):
            nuit.d["merges"].append({"quand": maintenant().isoformat(), "texte": phrase})
        if not ok:
            nuit.incident(f"le portier a rencontré une erreur ({bilan[:200]}) ; il réessaiera après le prochain créneau.")
        nuit.sauver()
    return bilan


def secondes_avant_fin_de_nuit() -> float | None:
    """Pour une équipe programmée : secondes jusqu'à FIN_NUIT ; 0 si on est en journée ; None si lancée à la main."""
    if os.environ.get("GITHUB_EVENT_NAME") != "schedule":
        return None
    t = maintenant()
    h_fin, m_fin = (int(x) for x in FIN_NUIT.split(":"))
    h_deb, m_deb = (int(x) for x in DEBUT_NUIT.split(":"))
    fin = t.replace(hour=h_fin, minute=m_fin, second=0)
    debut = t.replace(hour=h_deb, minute=m_deb, second=0)
    if fin <= t < debut:
        return 0
    if t >= debut:
        fin += dt.timedelta(days=1)
    return (fin - t).total_seconds()


def mode_nuit(un_seul: bool = False) -> int:
    fin_equipe = DEBUT + DUREE_EQUIPE_MIN * MINUTE
    avant_fin = secondes_avant_fin_de_nuit()
    if avant_fin is not None:
        if avant_fin < 45 * 60:
            journal("C'est la journée (ou presque) : l'équipe de nuit ne démarre pas, pour laisser à Ange son quota.")
            return 0
        fin_equipe = min(fin_equipe, time.monotonic() + avant_fin)
    nuit = Nuit()
    nuit.sauver()
    if not stack_prete():
        nuit.incident("la stack Docker ne démarre pas (voir logs/docker.log) : l'équipe ne peut pas tester, elle s'arrête.")
        nuit.terminer("stack Docker en panne")
        sauver_etat(f"Équipe de nuit du {nuit.cle} : arrêt, Docker en panne")
        notifier("Équipe d'agents", "Nuit annulée : la stack Docker ne démarre pas.")
        return 1

    if not EN_CLOUD:
        mode_courrier(interne=True)
    portier(nuit)  # une PR approuvée pendant la journée part tout de suite
    planifications, coupes_quota, raison = 0, 0, "heure de fin"
    if un_seul:
        nuit.d["creneaux"].append({"n": len(nuit.d["creneaux"]) + 1, "type": "auto", "cible": "auto",
                                   "titre": "tâche prioritaire", "minutes": 60, "statut": "a_faire", "tentatives": 0})
        executer_creneau(nuit, nuit.d["creneaux"][-1], fin_equipe)
        portier(nuit)
        nuit.terminer("créneau unique")
        sauver_etat(f"Équipe : créneau unique du {nuit.cle}")
        publier_livrables()
        return 0
    while True:
        if time.monotonic() > fin_equipe - 15 * MINUTE:
            raison = "heure de fin de l'équipe"
            break
        etat, attente = decision_quota(fin_equipe)
        if etat == "stop":
            raison = "part du quota Claude atteinte"
            nuit.incident("l'équipe a atteint sa part du quota Claude : elle s'arrête pour laisser ta part intacte.")
            break
        if etat == "attendre":
            nuit.incident(f"limite d'usage des 5 heures atteinte : pause de {attente // 60} min, puis reprise.")
            sauver_etat(f"Équipe de nuit du {nuit.cle} : pause quota")
            time.sleep(attente)
            continue
        mettre_a_jour()
        if nuit.a_faire() and nuit.d.get("empreinte_consignes") not in (None, empreinte_consignes()):
            # L'organisateur a changé le plan ou reçu une consigne d'Ange : on replanifie le reste
            for c in nuit.a_faire():
                c["statut"] = "reporte"
            nuit.incident("nouvelles consignes de l'organisateur : le chef d'équipe refait le planning.")
        if not nuit.a_faire():
            if planifications >= 3:
                raison = "planning épuisé"
                break
            planifications += 1
            if not planifier(nuit, int((fin_equipe - time.monotonic()) / MINUTE)):
                raison = "plus de tâche prête"
                break
            sauver_etat(f"Équipe de nuit du {nuit.cle} : planning")
            continue
        if not stack_prete():
            nuit.incident("la stack Docker s'est arrêtée et ne redémarre pas : l'équipe s'arrête.")
            raison = "stack Docker en panne"
            break
        creneau = nuit.a_faire()[0]
        executer_creneau(nuit, creneau, fin_equipe)
        coupes_quota = coupes_quota + 1 if creneau["statut"] == "quota" else 0
        sauver_etat(f"Équipe de nuit du {nuit.cle} : créneau {creneau['n']}")
        portier(nuit)
        sauver_etat(f"Équipe de nuit du {nuit.cle} : créneau terminé")
        publier_livrables()
        if coupes_quota >= 2:
            raison = "limite d'usage Claude"
            nuit.incident("deux créneaux de suite coupés par la limite d'usage : l'équipe s'arrête jusqu'à la prochaine équipe.")
            break

    nuit.terminer(raison)
    sauver_etat(f"Équipe de nuit du {nuit.cle} : fin ({raison})")
    publier_livrables()
    faits = sum(c["statut"] == "fait" for c in nuit.d["creneaux"])
    notifier("Équipe d'agents", f"Fin de l'équipe ({raison}) : {faits} créneau(x) terminé(s), "
                                f"{len(nuit.d['merges'])} livraison(s), {len(nuit.d['incidents'])} incident(s).")
    return 0


# ---------------------------------------------------------------------------
# Courrier, matin, pilotage, rapport
# ---------------------------------------------------------------------------
def mode_courrier(interne: bool = False) -> int:
    try:
        messages = bureau.preparer_courrier()
    except Exception as e:  # noqa: BLE001
        journal(f"Courrier illisible : {e}")
        return 0 if interne else 1
    if not messages:
        journal("Aucun nouveau message d'Ange.")
        return 0
    reponse = LOGS / "reponse-courrier.md"
    reponse.unlink(missing_ok=True)
    s = session_claude("/courrier", "organisateur-courrier", 30)
    if reponse.exists() and reponse.read_text(encoding="utf-8").strip():
        if bureau.poster(bureau.ouvrir(), reponse.read_text(encoding="utf-8")):
            bureau.marquer_repondus(messages)
    else:
        journal(f"L'organisateur n'a pas écrit de réponse (session : code {s.code}) ; nouvel essai au prochain passage.")
    revenir_sur_master("Courrier")
    if not interne:
        sauver_etat("Organisateur : réponse au courrier d'Ange")
        publier_livrables()
    return 0


def mode_matin() -> int:
    mode_courrier(interne=True)  # rattrapage si une réponse a échoué
    bureau.matin()
    sauver_etat("Organisateur : rapport du matin")
    return 0


def semaine() -> str:
    return maintenant().strftime("%G-S%V")


def mode_pilotage() -> int:
    s = session_claude(f"/cycle-pilotage {semaine()}", "organisateur-pilotage", 60)
    revenir_sur_master("Pilotage")
    if not s.reussie:
        notifier("Équipe d'agents", "Le pilotage du dimanche s'est arrêté avant la fin : le rapport ne contiendra "
                                    "que les chiffres.")
    sauver_etat(f"Organisateur : pilotage {semaine()}")
    mode_rapport(publier=True)
    publier_livrables()
    return 0


def mode_rapport(publier: bool = False) -> int:
    cmd = [sys.executable, "scripts/rapport.py", "--semaine", semaine()] + (["--publier"] if publier else [])
    ok, sortie = lancer(cmd, timeout=900)
    print(sortie)
    if not ok:
        notifier("Équipe d'agents", f"Rapport {semaine()} non généré : {sortie[-300:]}")
    publier_livrables()
    return 0 if ok else 1


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    modes = {"nuit": mode_nuit, "tech": lambda: mode_nuit(un_seul=True), "courrier": mode_courrier,
             "matin": mode_matin, "pilotage": mode_pilotage, "rapport": mode_rapport}
    if mode not in modes:
        print(f"Usage : {sys.argv[0]} {'|'.join(modes)}", file=sys.stderr)
        return 2
    _verrou = verrou()  # noqa: F841 - gardé jusqu'à la fin du processus
    preparer(mode)
    try:
        return modes[mode]()
    finally:
        revenir_sur_master("Fin")


if __name__ == "__main__":
    sys.exit(main())
