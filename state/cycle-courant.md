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
- Cycle : tech du 2026-10-18
- Issue / PR : #2 → PR #14 **en brouillon** (https://github.com/angemevo/Blueprint_Academy/pull/14), ouverte par le `developpeur`
- Branche : `feat/2-interfaces-validation` (poussée, 399 lignes modifiées, aucune migration)
- État : pytest 78/78, ruff OK, makemigrations --check OK, lint frontend OK. `npm run typecheck` **échoue** sur `.next/dev/types/validator.ts`, généré par `next dev` dans le conteneur (TS6196 / TS6133). La PR ne touche aucun fichier frontend, donc l'échec existe aussi sur `master`. Il est hors périmètre de #2 : la PR est en brouillon pour cette seule raison.
- Verdict qa : **OK** (publié en commentaire sur la PR, sous la forme `VERDICT : APPROUVÉE`). La qa a relancé les vérifications sur le commit `e8cc439` : le typecheck échoue de la même façon sur `master`, il est donc hors périmètre. Cause : `frontend/tsconfig.json` inclut `.next/dev/types/**/*.ts` et active `noUnusedLocals`. Le brouillon `logs/revue-14.md` n'a pas été écrit, faute des outils Write et Edit côté qa.
- Remarques non bloquantes : (1) le docstring de `HintService` présente l'indice comme la « seule voie » par laquelle la solution atteint le client, ce qui est plus strict que CLAUDE.md et reste à confirmer par Ange ; (2) `frozen=True` ne fige pas le contenu des listes `feedback` et `hints` ; (3) les validateurs de #3 et #4 devront avoir un constructeur sans paramètre et ne s'importer que sous un seul nom de module.
- Prochaine action : Ange passe #14 en « ready » (`gh pr ready 14`) et la merge. Ensuite : ouvrir une issue d'outillage pour le typecheck, et poser `ready` sur #3 une fois sa règle de score validée. Le plan S42 est épuisé : le prochain cycle de pilotage établit le plan S43.
- Hors cycle : la PR #13 « Sécurité : mise à jour de Next.js (npm audit fix) » (`fix/securite-dependances`, ouverte par angemevo le 2026-10-18) n'a pas encore de revue qa.

## Tâche précédente
- Cycle : tech du 2026-10-16 (terminé)
- Issue / PR : #1 → PR #12 (https://github.com/angemevo/Blueprint_Academy/pull/12), ouverte par le `developpeur`
- Branche : `feat/1-outillage-qualite` (poussée)
- État : vérifications toutes au vert, relancées par la qa (ruff, lint, pytest 48/48, makemigrations --check, typecheck). E501 ignorée et migrations exclues dans `ruff.toml` (justifié dans la PR). `npm install` signale 8 vulnérabilités (7 élevées, 1 critique). Selon la qa, aucune dépendance d'exécution n'est ajoutée, mais l'origine reste non vérifiée (`npm audit` refusé).
- Verdict qa : **OK** (revue publiée sur la PR, texte dans `logs/revue-12.md`). Remarques non bloquantes : épingler `ruff>=0.17,<0.18` ; aligner `eslint-config-next` (16.4.2) sur `next` (16.3.5).
- Prochaine action : Ange merge la PR #12 (voir `state/validations.md`). Le prochain cycle tech prend #2 (branche `feat/2-interfaces-validation`), qui devra passer `ruff check .` si #12 est mergée.
