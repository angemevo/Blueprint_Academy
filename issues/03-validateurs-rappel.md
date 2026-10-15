Titre: Validateurs des types de rappel et de transition (A, B, C, D)
Labels: phase-2b,backend
---
**Dépend de :** #02 (interfaces de validation)

## Pourquoi
Les échauffements doivent pouvoir être corrigés côté serveur. Ce sont les validateurs les plus simples : un bon premier test du registre.

## Ce qui est attendu
Un validateur par type, enregistré dans le registre, qui lit la `solution` au format défini par `apps/exercises/schemas/interactive.py` :

- **A — Question** : réponse comparée à `accepted_answers` après suppression des espaces en bord et des espaces multiples ; insensible à la casse sauf si `case_sensitive` est vrai.
- **B — QCM** : correct si l'ensemble des options choisies est exactement `correct_option_ids`.
- **C — Ordre** : correct si l'ordre soumis est exactement `order`.
- **D — Node matching** : correct si toutes les paires de `pairs` sont trouvées.

**Règle de score proposée (à confirmer par Ange avant `ready`)** : A et B tout-ou-rien (100 ou 0) ; C = part des éléments à la bonne position ; D = part des paires correctes. `is_correct` n'est vrai qu'à 100.

- Une soumission mal formée (champ manquant, identifiant inconnu) renvoie un `ValidationResult` incorrect avec un feedback lisible, jamais une exception non gérée.
- Le feedback ne révèle jamais la solution.

## Critères d'acceptation
- [ ] Tests unitaires pour chaque type : réponse juste, fausse, partielle (C, D), mal formée.
- [ ] Le texte du feedback ne contient aucune réponse attendue (test dédié).

## Hors périmètre
- Types de production (E à I).
- Persistance des tentatives.
