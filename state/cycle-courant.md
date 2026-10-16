# Cycle courant

## Plan de la semaine (2026-S42, du 12 au 18 octobre)

Aucune issue planifiée cette semaine.

Raison : aucune issue n'a pu être vérifiée comme portant l'étiquette `ready`.
- Pendant le cycle de pilotage du 2026-10-16, l'accès à GitHub (`gh`) a été refusé : l'espace de travail n'est pas marqué comme approuvé, donc les autorisations de `.claude/settings.json` sont ignorées en mode headless (voir `logs/2026-10-16_1114-pilotage.json`).
- `state/validations.md` ne montre aucune case cochée par Ange, notamment pas le point « Poser `ready` sur les issues sans dépendance ».

Le cycle tech n'a donc rien à prendre. Il doit écrire « Plan de la semaine terminé » et s'arrêter.

## Candidats pour le prochain plan (pas planifiés, en attente de `ready`)

Ces issues entrent au plan dès qu'Ange a posé `ready` et que le pilotage a été relancé avec l'accès à `gh`. Ordre recommandé :

1. Issue « Outillage qualité : ruff (backend) et ESLint (frontend) » : fichier `issues/01-outillage-qualite.md`, numéro GitHub présumé #1, à confirmer. Dépend de : aucune.
2. Issue « Interfaces de validation et registre des validateurs » : fichier `issues/02-interfaces-validation.md`, numéro GitHub présumé #2, à confirmer. Dépend de : aucune.

Ensuite : issue « Authentification JWT » (`issues/05-auth-jwt.md`, numéro présumé #5), une fois la question de la blacklist tranchée.

Les numéros présumés supposent que `scripts/creer-issues.sh` a été lancé une seule fois, sur un dépôt sans issue ni PR antérieure. Ils doivent être vérifiés sur GitHub.

## Dernière tâche traitée
- Issue / PR : aucune
- Branche : aucune
- Verdict qa : aucun
- Prochaine action : Ange rend `gh` accessible au mode headless, pose `ready` sur les issues retenues, puis relance `scripts/cycle.sh pilotage`.
