# Cycle courant

## Plan de la semaine (2026-S44, du 26 octobre au 1er novembre) : mise à jour du pilotage du 2026-10-25

Ordre de traitement (toutes `ready`) :
1. **#11 « Calcul de la maîtrise des skills »** (backend, formule validée par Ange le 2026-10-25).
2. **#31 « Socle du site : thème sombre, navigation, session »** (frontend).
3. **#32 « Écrans d'inscription et de connexion »**, dépend de #31.
4. **#33 « Vitrine publique : accueil, catalogue et détail d'un parcours »**, dépend de #31.
5. **#34 « Page de leçon et navigation dans le module »**, dépend de #31.

Hors plan : #4 (`a-cadrer`, cadrage à refaire depuis les captures d'Ange, cas « à vérifier dans Unreal »). Plus de type I au MVP. Quota hebdo à 63 % : plan limité à 5 issues.
Questions en attente d'Ange : Q1, Q2 (non bloquantes, échéance 2026-11-01).

(Ancien plan ci-dessous, conservé pour l'historique.)

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

## Issue #11
Branche feat/11-maitrise-skills, PR #36, en attente de relecture QA.

## Reprise PR #36 (issue #11) : CORRECTIONS demandées par qa
Voir `gh pr view 36` / revue : ajouter un test de bout en bout de `submit_exercise` avec un validateur de production factice (la maîtrise bouge pour E/F/G/H, pas pour A/B), et corriger le nom du test « reaches_100 » qui vérifie 94.

- Créneau 1 (2026-10-25) : issue #11 (maîtrise des skills), branche feat/11-maitrise-skills, PR #36 ouverte (non brouillon), qa APPROUVÉE après une boucle de corrections (226 tests OK). Prochaine action : le portier merge #36.

- Créneau 2 (2026-10-25) : issue #31, PR #37 ouverte (non brouillon), qa APPROUVÉE (tests, typecheck, lint, build OK). Non bloquant : restreindre `next` aux chemins relatifs (issue connexion), accents manquants dans quelques textes. Prochaine action : le portier merge #37.

- Créneau 3 (2026-10-25) : issue #32, PR #38 ouverte (non brouillon), qa APPROUVÉE (pytest 226, tests frontend 9, typecheck et lint OK). Réserve non bloquante : textes côté client sans accents. Prochaine action : le portier merge #38.

- Créneau 4 (2026-10-25) : issue #33, branche feat/33-vitrine-publique, PR #39 ouverte (non brouillon), qa APPROUVÉE (frontend 14 tests OK). Non bloquant : accents manquants dans les textes, détail rendu à la demande. Prochaine action : le portier merge #39.

- Créneau 5 (2026-10-25) : issue #34, branche feat/34-page-lecon, PR #40 ouverte (non brouillon), qa APPROUVÉE (226 tests backend, 19 frontend OK). Prochaine action : le portier merge #40.

## Réapprovisionnement (2026-10-25, nuit)
#11 et #31 à #34 mergées et fermées. Nouvelles issues `ready`, dans l'ordre : #41 (espace d'exercice, types A et B) -> #42 (ordre, glisser-déposer) -> #43 (association) -> #44 (tableau de bord). #42 et #43 dépendent de #41. Hors plan : #4 (`a-cadrer`). Canvas Blueprint : à écrire au prochain passage, après #41.

- Issue #41 : branche feat/41-exercise-workspace, PR ouverte, en attente de qa.
- Créneau 6 (2026-10-25) : issue #41, branche feat/41-exercise-workspace, PR #45 ouverte (non brouillon), qa APPROUVÉE (typecheck, lint, 26 tests front, 226 tests back OK). Prochaine action : le portier merge #45.

- Créneau 7 (2026-10-25) : issue #42, branche feat/42-exercice-ordre-dnd, PR #46 ouverte (non brouillon), qa APPROUVÉE (28 tests frontend, 226 backend OK). Réserve non bloquante : glisser-déposer souris/clavier non simulé dans les tests. Prochaine action : le portier merge #46.

- Créneau 8 (2026-10-25) : issue #43, branche feat/43-exercice-association-dnd, PR #47 ouverte (non brouillon), qa APPROUVÉE (227 tests backend, 30 tests frontend OK). Réserves non bloquantes : test de mélange peu probant avec 2 paires, pas de signal visuel au remplacement d'un partenaire. Prochaine action : le portier merge #47.

- Créneau 9 (2026-10-25) : issue #44, branche feat/44-tableau-de-bord, PR #48 ouverte (non brouillon), qa APPROUVÉE (34 tests frontend, 227 backend OK). Réserves non bloquantes : barre XP = total/seuil suivant, lien « Continuer » via le premier parcours. Prochaine action : le portier merge #48.

## Réapprovisionnement (2026-10-25, 2e passe)
#41 à #44 mergées (PR #45 à #48) et fermées. Nouvelles issues `ready`, dans l'ordre : #49 (pins dans le catalogue, backend) -> #50 (canvas en lecture seule, dépend de #49) -> #51 (canvas : ajout de nodes et liens, dépend de #50). Hors plan : #4 (`a-cadrer`). Ensuite : soumission des exercices de construction (attend #4), phase 4 (admin) seulement après accord d'Ange.

- Créneau 10 (2026-10-25) : issue #49, branche feat/49-pins-catalogue, PR #52 ouverte (non brouillon), qa APPROUVÉE (230 tests OK). Réserves non bloquantes : test manquant sur les clés du tableau de pins ; API ne signale pas les pins non confirmés. 45 nodes sans pins, noms « à vérifier dans Unreal ». Prochaine action : le portier merge #52.

- Créneau 11 (2026-10-25) : issue #50, branche feat/50-canvas-lecture-seule, PR #53 ouverte (non brouillon), qa APPROUVÉE (230 tests backend, 39 frontend OK). Prochaine action : le portier merge #53.

- Issue #51 : branche feat/51-canvas-edition, PR #54, en attente de relecture QA.

- Issue #51 / PR #54 : qa CORRECTIONS (4 points dans logs/revue-54.md : properties perdues dans la sortie, couleur des liens, test de node verrouillé, taille < 400). Le developpeur reprend la PR au prochain cycle.

- Issue #51 / PR #54, 2e relecture : qa CORRECTIONS, un seul point restant (taille 465 lignes > 400, resserrer ou justifier dans le corps de la PR ; voir logs/revue-54.md). Points 1 à 3 corrigés.

- Créneau 12 (2026-10-25) : issue #51, branche feat/51-canvas-edition, PR #54 ouverte (non brouillon), qa CORRECTIONS (2 passes). Points 1 à 3 corrigés ; reste la taille (465 lignes pour une cible de 400) : resserrer ou corriger le corps de la PR avec le chiffre réel. Prochaine action : reprise du développeur, puis qa.

- Créneau 1 (2026-10-28) : reprise PR #54 (issue #51, canvas Blueprint éditable). Corps de PR mis à jour (taille réelle ~465 lignes, raison de ne pas découper), qa APPROUVÉE (230 tests backend, 46 tests frontend OK). Prochaine action : le portier merge #54.
