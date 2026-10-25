# Cycle courant

## Plan de la semaine (2026-S44, du 26 octobre au 1er novembre)

Établi par le pilotage du 2026-10-20, vérifié sur GitHub. Aucune réponse d'Ange (pas de point hebdo publié). Quota : aucun cycle coupé la semaine passée, le plan peut compter plus de 4 issues.

Ordre de traitement :

1. **#15 « Typecheck frontend : ignorer les types générés par next dev »** (`ready`, outillage). Dépend de : aucune. Débloque la vérification obligatoire pour toutes les PR : en premier.
2. **#5 « Authentification JWT »** (`ready`, backend). Dépend de : aucune. Blacklist JWT activée (décision du 2026-10-20) ; migration de `token_blacklist` permise. Tête du chemin critique (#5 → #6 → #7 → #8 → #9). Étant visible par Ange via l'API (inscription, connexion), elle passe avant #16.
3. **#16 « Épingler ruff sur une version mineure »** (`ready`, outillage). Dépend de : aucune. Petite.

Candidates si les dépendances sont mergées en cours de semaine :
4. **#3 « Validateurs A, B, C, D »** : dépend de #2 (PR #14) et de la réponse à Q1 (par défaut le 2026-10-25, `ready` alors posé par le pilotage).
5. **#6 « Profil courant et permissions »** : dépend de #5 mergée.

À traiter en priorité par le cycle tech, avant le plan :
- **PR #14 (issue #2)** : verdict qa APPROUVÉE, mais encore en brouillon. L'orchestrateur n'a pas pu faire `gh pr ready 14` (approbation requise en mode headless). Si le cycle tech ne le peut pas non plus, la PR attend que quelqu'un la passe en « prête » ; le portier la mergera ensuite si les vérifications passent. Le typecheck échoue sur `master` : #15 le corrige.
- **PR #13 (Next.js, lockfile)** : sans revue qa, ne corrige pas le typecheck contrairement à ce que dit sa description. À relire.

Hors plan : #4 et #11 (`a-cadrer`), #7 à #10 (dépendances non mergées).

## Dernière tâche traitée
- #15, branche fix/15-typecheck-next-dev-types, PR #17 ouverte (non brouillon), qa APPROUVÉE (2026-10-21, verdict publié par le pilote du cycle car qa n'a pas pu écrire). Réserve : cas « .next/dev/types présent » non observé directement. Aucune réponse d'Ange à lire (pas de point hebdo ouvert).
- Prochaine action : le portier merge #17 ; ensuite #5, puis #16. Restent à traiter : PR #14 (brouillon, à passer en « prête ») et PR #13 (sans revue qa).
- Créneau 1 (2026-10-21) : revue de la PR #13 (mise à jour de sécurité de Next.js), qa APPROUVÉE. Réserve non bloquante : la description de la PR parle d'une exclusion dans tsconfig.json que le diff ne contient pas (déjà sur master via #17). Prochaine action : le portier merge #13.
- Cycle : tech du 2026-10-18, #2 → PR #14 en brouillon, qa APPROUVÉE.

- Créneau 4 (2026-10-21) : issue #5, branche feat/5-auth-jwt, PR #18 ouverte (non brouillon), qa APPROUVÉE (91 tests OK). Prochaine action : le portier merge #18.

- Créneau 6 (2026-10-21) : issue #16, branche fix/16-epingler-ruff, PR #19 ouverte (non brouillon), qa APPROUVÉE (ruff~=0.17.0, 91 tests OK). Prochaine action : le portier merge #19.

## Issue #6
Branche feat/6-profil-permissions, PR #21, prête pour revue.
- Créneau 1 (2026-10-22) : issue #6, branche feat/6-profil-permissions, PR #21 ouverte (non brouillon), qa APPROUVÉE (101 tests OK). Prochaine action : le portier merge #21.

- Issue #7 : branche feat/7-api-catalogue, PR #22, ouverte (vérifications passées).

- Créneau 4 (2026-10-22) : issue #7, branche feat/7-api-catalogue, PR #22 ouverte (non brouillon), qa APPROUVÉE (110 tests OK). Prochaine action : le portier merge #22.

## Issue #8
- Branche feat/8-api-exercices, PR #23, prête pour relecture.

- Créneau 6 (2026-10-22) : issue #8, branche feat/8-api-exercices, PR #23 ouverte (non brouillon), qa APPROUVÉE (145 tests OK). Réserve non bloquante : le type D n'est pas mélangé (l'ordre des colonnes peut révéler les paires), à traiter avec la soumission. Prochaine action : le portier merge #23.

- Créneau 1 (2026-10-23) : issue #3, branche feat/3-validateurs-abcd, PR #24 ouverte (non brouillon), qa APPROUVÉE (184 tests OK). Prochaine action : le portier merge #24.

## Réapprovisionnement (2026-10-23)
Nouvelles issues `ready`, dans l'ordre : #9 (soumission) -> #10 (XP et niveaux, courbe validée par Ange) -> #25 (progression et prérequis) -> #26 (données du tableau de bord). Hors plan : #4 et #11 (`a-cadrer`, attendent Ange / exports du 24 octobre).

- Créneau 2 (2026-10-23) : issue #9, branche feat/9-soumission-exercice, PR #27 ouverte (non brouillon), qa APPROUVÉE (196 tests OK). Prochaine action : le portier merge #27. Point à trancher dans l'issue XP : la limite d'essais compte aussi les tentatives réussies.

- Créneau 3 (2026-10-23) : issue #10, branche feat/10-xp-niveaux, PR #28 ouverte (non brouillon), qa APPROUVÉE (201 tests OK). Réserve non bloquante : pas de test de concurrence. Prochaine action : le portier merge #28.

- Créneau 4 (2026-10-23) : issue #25, branche feat/25-*, PR #29 ouverte (non brouillon), qa APPROUVÉE (207 tests OK, aucune migration). Réserve non bloquante : requêtes multiples par leçon dans la vue d'ensemble. Prochaine action : le portier merge #29.

- Créneau 5 (2026-10-23) : issue #26, branche feat/26-dashboard-api, PR #30 ouverte (non brouillon), qa APPROUVÉE (212 tests OK). Prochaine action : le portier merge #30.

## Réapprovisionnement (2026-10-23, 2e passe)
Toute la phase 2 prête est mergée (#2 à #10, #25, #26 fermées). Rien n'est `ready`. Restent #4 (exports Unreal du 24 octobre), #11 (formule proposée en commentaire, attend Ange), lecture d'un export Unreal. Question Q6 posée : passer à la phase 3. Aucune issue de la phase 3 écrite avant accord (règle « attendre validation »).

## Réapprovisionnement (2026-10-24)
Rien de nouveau : Q6 (phase 3) sans réponse, échéance 2026-11-01 ; #4 et #11 attendent Ange (exports Unreal du jour, formule de maîtrise). Aucune issue écrite.

## Consigne d'Ange (2026-10-25)
Plan mis à jour : 1. #11 (maîtrise, formule validée) ; 2. #31 socle du site ; 3. #32 écrans connexion ; 4. #33 vitrine ; 5. #34 page de leçon. #4 reste `a-cadrer` (exports Unreal en texte attendus).
