Titre: Attribution d'XP par le ledger et calcul du niveau
Labels: phase-2b,backend
---
**Dépend de :** #09 (soumission)

## Ce qui est attendu
- Un service de l'app `gamification` qui, à la **première** réussite d'un exercice, écrit une `XPTransaction` (`source = exercise_solved`, ou `challenge_solved` pour le type G ; `reference_key = "exercise:<id>"`) du montant `Exercise.effective_xp_reward`.
- Idempotence garantie par la contrainte unique existante : une seconde réussite ne crée rien.
- Mise à jour du cache `Profile.total_xp` et `Profile.level` dans la même transaction.
- Appel depuis le service de soumission.
- Une commande `recompute_xp` qui recalcule les caches à partir du ledger.

**Décision à valider par Ange avant `ready`** : la courbe de niveaux. Proposition : un réglage `XP_LEVEL_THRESHOLDS` (liste d'XP cumulée par niveau) dans les settings, configurable comme le barème.

## Critères d'acceptation
- [ ] Double réussite → une seule transaction (test).
- [ ] `recompute_xp` restaure un cache volontairement faussé (test).
- [ ] Aucun montant ni seuil écrit en dur dans le code.

## Hors périmètre
- Maîtrise des skills (issue dédiée), séries, achievements.
