# Cycle courant

## Plan de la semaine (2026-S42, du 12 au 18 octobre)

Établi par le pilotage du 2026-10-16 (3e cycle du jour). Vérifié sur GitHub avec des commandes `gh` simples :
- `ready` posé sur #1 et #2. Retiré de #10 et #11 (mis à jour sur GitHub le 2026-10-16 vers 19 h 22).
- Aucune issue fermée, aucune PR (ni ouverte ni mergée).
- Quota : la semaine précédente n'a eu aucun cycle, donc aucun cycle coupé. Le plan peut compter 2 issues.

Ordre de traitement :

1. **#1 « Outillage qualité : ruff (backend) et ESLint (frontend) »**
   - Dépend de : aucune. Étiquettes : `ready`, `phase-2b`, `outillage`.
   - L'issue autorise explicitement la modification de `requirements-dev.txt`, de `package.json` et du lockfile. Le lockfile se régénère **dans le conteneur**.
   - Passe en premier : une fois #1 mergée, le lint devient une vérification obligatoire pour toutes les PR suivantes, #2 comprise (`.claude/equipe.md`).
2. **#2 « Interfaces de validation et registre des validateurs »**
   - Dépend de : aucune. Étiquettes : `ready`, `phase-2b`, `backend`.
   - Si #1 est mergée avant la fin de #2 : rebaser sur `master`, puis faire passer `ruff check .` avant d'ouvrir la PR. Si #1 n'est pas mergée, #2 ne doit pas attendre : elle est indépendante.
   - Ouvre la chaîne de validation (#2 → #3 → #9).

Hors plan, à ne pas prendre : #3 à #11 (sans `ready`, ou avec des dépendances non mergées). #4 et #11 sont `a-cadrer`.

## Candidats pour le prochain plan (S43, en attente de `ready`)

1. #5 « Authentification JWT ». Dépend de : aucune. Préalable : décision blacklist (`state/validations.md`). C'est la tête du chemin critique (#5 → #6 → #7 → #8 → #9).
2. #3 « Validateurs A, B, C, D ». Dépend de : #2. Préalable : règle de score validée et #2 mergée.

## Dernière tâche traitée
- Cycle : pilotage du 2026-10-16 (3e cycle du jour)
- Issue / PR : aucune (pilotage)
- Branche : aucune
- Verdict qa : aucun
- Prochaine action : le cycle tech prend #1 (branche `feat/1-outillage-qualite`), puis #2 (branche `feat/2-interfaces-validation`).
