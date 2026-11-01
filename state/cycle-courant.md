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

- Tâche : #61 « Admin de contenu : parcours, modules, leçons, exercices » (créneau 1, 2026-11-01).
- PR : #64 (non brouillon, `Closes #61`).
- Verdict de qa : APPROUVÉ. Remarques non bloquantes à traiter avec #62 : message « modifié avec succès » trompeur quand la publication est refusée ; test de publication refusée trop permissif ; une leçon publiée créée dans l'admin saute le contrôle d'intégrité (clé primaire absente).
- Prochaine action : le portier merge #64, puis #62.
