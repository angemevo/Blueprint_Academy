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
