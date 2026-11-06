# Cycle courant

## Plan de la semaine (2026-S45, du 2 au 8 novembre) : pilotage du 2026-11-01

Phase 4 (administration) acceptée par défaut. Quota hebdo à 22 % : pas de limite sur le plan.

Ordre de traitement (toutes `ready`) :
1. **#61 « Admin de contenu : parcours, modules, leçons, exercices »** (backend). Dépend de : aucune.
2. **#62 « Admin : publication avec contrôle d'intégrité »** (backend). Dépend de : #61.

Hors plan : #4 (`a-cadrer`, attend la validation par Ange des cas « à vérifier dans Unreal »). Plus de type I au MVP.
Prochains lots après la phase 4 (pas encore d'issue) : tests de bout en bout (phase 6), Docker (7), documentation (8). La phase 5 (parcours de départ) attend Ange (Q2).
Questions en attente d'Ange : Q1, Q2 (non bloquantes, échéance 2026-11-08).

## Dernière tâche traitée

- Tâche : #62 « Admin : publication avec contrôle d'intégrité » (créneau 2, 2026-11-01).
- PR : #65 (non brouillon, `Closes #62`).
- Verdict de qa : APPROUVÉE. Remarques non bloquantes : le contrôle voit les anciens skills si on les modifie dans le même formulaire que la case « publié » ; trois lignes vides dans `common/admin.py`. Hors périmètre : publication d'un exercice non contrôlée.
- Prochaine action : le portier merge #65.

## Réapprovisionnement 2026-11-01

Phase 4 terminée. Aucune issue `ready` : la phase 5 attend Ange (Q3). Rien à planifier avant sa réponse ou le 2026-11-08. (Revérifié en fin de journée du 2026-11-01 : aucune réponse d'Ange, aucune issue `ready` restante ; #61 et #62 sont faites et seront refermées par leur PR.)

## Réapprovisionnement 2026-11-04

Aucune issue `ready` possible : phase 4 finie, Q3 (phase 5) sans réponse avant le 2026-11-08, #4 attend Ange. Aucun changement au plan.

## Réapprovisionnement 2026-11-05 (second passage)

Revérifié : bureau sans message d'Ange, seules #4 (`a-cadrer`) et le bureau sont ouvertes. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-05

Toujours aucune réponse d'Ange (Q1 à Q3), aucune issue `ready` possible. Aucun changement au plan ; décisions par défaut le 2026-11-08.

## Réapprovisionnement 2026-11-06

Bureau sans message d'Ange, Q1 à Q3 sans réponse (échéance 2026-11-08, pas encore passée). Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-06 (second passage)

Même constat : seules #4 (`a-cadrer`) et le bureau sont ouvertes, échéance des questions non passée. Aucune issue `ready` possible. Plan inchangé.
