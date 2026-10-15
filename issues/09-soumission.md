Titre: Soumission d'un exercice et enregistrement des tentatives
Labels: phase-2b,backend
---
**Dépend de :** #03 (validateurs de rappel), #08 (API exercices)

## Ce qui est attendu
- `POST /api/exercises/{id}/submit/` avec `submission`, `duration_seconds` et `hints_used` optionnels.
- Un service de l'app `exercises` qui, **dans une transaction** :
  1. verrouille les tentatives de l'utilisateur sur l'exercice (`select_for_update`) et alloue `attempt_number` ;
  2. refuse au-delà de `max_attempts` (409) ;
  3. récupère le validateur par le registre ; type sans validateur → 501 avec un message clair ;
  4. enregistre l'`ExerciseAttempt` complet (soumission, score, feedback, durée, indices) ;
  5. renvoie le `ValidationResult` sérialisé.
- La réponse ne contient jamais la solution.

## Critères d'acceptation
- [ ] Deux soumissions simultanées obtiennent des numéros différents (test avec deux transactions, ou vérification de la contrainte unique).
- [ ] `max_attempts` respecté (test).
- [ ] Types E à I → 501 tant que #04 n'est pas livré (test).

## Hors périmètre
- XP et maîtrise (issues dédiées) : la soumission ne les modifie pas encore.
