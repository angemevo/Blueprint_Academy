Titre: Interfaces de validation et registre des validateurs
Labels: phase-2b,backend
---
**Dépend de :** aucune

## Pourquoi
CLAUDE.md impose un registre `exercise_type → Validator` et une interface commune `validate(exercise, submission) -> ValidationResult`. C'est la fondation de toute la soumission d'exercices.

## Ce qui est attendu
- Dans `apps/validation` : la dataclass `ValidationResult(is_correct: bool, score: int, feedback: list, hints: list)` (score borné 0–100, vérifié à la construction) et le protocole `Validator`. Aucun modèle, aucune requête base.
- Dans `apps/exercises/validators/` : le registre (`register` en décorateur, `get_validator(exercise_type)`), indexé par les valeurs de `ExerciseType` de `apps/exercises/enums.py`, sans redéclarer la liste des types.
- Respecter l'isolement : tout import de `apps.validation` depuis `apps.exercises` reste **local à la fonction** (CLAUDE.md, « Architecture backend »).
- `get_validator` sur un type sans validateur lève une exception explicite (`UnsupportedExerciseType`).
- Interface `HintService` déclarée (protocole seulement, pas d'implémentation), comme prévu par CLAUDE.md.

## Critères d'acceptation
- [ ] Tests unitaires du registre : enregistrement, récupération, type inconnu, double enregistrement refusé.
- [ ] Tests de `ValidationResult` : score hors bornes refusé.
- [ ] Un test vérifie qu'aucun module de `apps/exercises` n'importe `apps.validation` au niveau module (analyse des imports avec `ast`).

## Hors périmètre
- Les validateurs concrets (issues suivantes).
- L'endpoint de soumission.
