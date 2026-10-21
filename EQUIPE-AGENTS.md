# Équipe d'agents — mise en route sur Blueprint Academy

> **L'équipe tourne désormais en autonomie sur GitHub, organisée autour d'un organisateur (ton seul interlocuteur), d'un chef d'équipe et d'un contrôleur** : voir [`docs/equipe-cloud.md`](docs/equipe-cloud.md). Ce qui suit décrit l'installation d'origine, sur ton ordinateur, devenue historique. On peut toujours lancer un créneau à la main avec `scripts/cycle.sh tech`, ou une nuit avec `scripts/cycle.sh nuit`.

Ce dépôt est le projet pilote de l'équipe d'agents (phase 1 : pôle Tech). Les agents développent et relisent ; Ange tranche et merge. Tout tourne avec Claude Code et l'abonnement Claude Pro.

## Ce qui a été ajouté

| Élément | Rôle |
| --- | --- |
| `.claude/equipe.md` | Règles de l'équipe, importées par `CLAUDE.md` |
| `.claude/agents/` | `organisateur`, `developpeur`, `qa` |
| `.claude/commands/` | `/planifier-nuit`, `/creneau`, `/courrier`, `/cycle-pilotage` |
| `.claude/settings.json` | Ce que les agents peuvent faire sans demander, et ce qui leur est interdit |
| `state/` | Mémoire de l'équipe : roadmap, cycle courant, décisions, validations, quota |
| `issues/` | Premier lot de 11 issues de la phase 2b |
| `scripts/creer-issues.sh` | Crée les étiquettes et les issues sur GitHub |
| `scripts/cycle.sh` | Lance un cycle sans toi (cron) |
| `.github/` | CI (backend et frontend) et modèles d'issue et de PR |
| `outils/salle-reunion/` | Interface pour suivre les cycles comme une réunion |

`CLAUDE.md` n'a reçu qu'une section de deux lignes à la fin, qui importe `.claude/equipe.md`.

## 1. Prérequis sur ton Ubuntu

```bash
# Docker utilisable sans sudo (nécessaire pour cron), puis redémarrer la session
sudo usermod -aG docker $USER

# Le projet doit démarrer
cp .env.example .env
docker compose up --build -d
docker compose exec -T backend pytest
```

## 2. Pousser le kit et protéger `master`

```bash
git add -A
git commit -m "Ajoute l'équipe d'agents (pôle Tech)"
git push
```

Sur GitHub, **Settings → Branches → Add rule** sur `master` : coche « Require a pull request before merging » et « Require status checks to pass » (jobs `backend` et `frontend`), sans cocher « Do not allow bypassing the above settings ». Tu restes ainsi capable de pousser l'état de l'équipe, et donc `cycle.sh` aussi.

## 3. Créer les issues (une seule fois)

```bash
scripts/creer-issues.sh
```

Puis traite `state/validations.md` : réponds aux questions des issues concernées et pose l'étiquette `ready` sur celles que tu acceptes. **Les agents ne prennent jamais une issue sans `ready`.**

## 4. Approuver le dossier pour Claude Code (une seule fois)

En mode automatique (`claude -p`), Claude Code ignore les autorisations de `.claude/settings.json` tant que tu n'as pas approuvé le dossier. Sans elles, les agents ne peuvent lancer ni `gh` ni les tests.

```bash
cd ~/Blueprint_Academy
claude          # accepte la question sur la confiance accordée au dossier, puis tape /exit
```

`scripts/cycle.sh` vérifie ce point et s'arrête avec un message clair s'il manque.

## 5. Premier cycle, à la main

```bash
scripts/cycle.sh pilotage   # plan de la semaine, file de validation, rapport
scripts/cycle.sh tech       # une issue développée puis relue
```

Pour suivre le cycle comme une réunion, ouvre la salle dans un autre terminal : `scripts/salle-reunion.sh` (voir `outils/salle-reunion/README.md`). Le résultat reste aussi sur GitHub : PR ouverte, commentaire `VERDICT : …` de l'agent qa.

## 6. Planifier

```bash
crontab -e   # colle scripts/crontab.exemple, avec le chemin du dépôt
```

Pour les notifications sur téléphone : app **ntfy**, un sujet secret, le même nom dans `NTFY_TOPIC`.

## Ta routine

| Quand | Quoi | Durée |
| --- | --- | --- |
| Mardi matin | Lire le rapport, traiter `state/validations.md`, poser `ready` | 15 min |
| Week-end | Relire et merger les PR approuvées par qa | 30 à 45 min |
| Après un merge qui change `requirements*.txt` ou `package.json` | Reconstruire les images (section « Après un changement de dépendances » du README) | 5 min |
| Fin de semaine 2 | Lire `state/quota.md` et ajuster le rythme | 5 min |

## Ce qui reste à toi

- Les issues `a-cadrer` : moteur de validation de graphe et formule de maîtrise. Ce sont le cœur pédagogique et le risque n° 1 du projet.
- Toute décision marquée « verrouillée » dans `CLAUDE.md`.
- La justesse du contenu Blueprint, vérifiée dans le vrai Unreal.

## Critère de passage à la phase 2 de l'équipe (pôle Run)

10 PR mergées, et deux semaines sans que le quota ne bloque ton usage personnel.
