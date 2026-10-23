"""Soumission d'un exercice : allocation du numero, validation, enregistrement.

L'XP est attribuee par le service de gamification a la premiere reussite ;
la maitrise reste hors perimetre (issue dediee).
"""

from dataclasses import asdict
from typing import Any

from django.db import transaction

from apps.exercises.models import Exercise, ExerciseAttempt
from apps.exercises.validators import UnsupportedExerciseType, get_validator


class MaxAttemptsReached(Exception):
    """Le nombre maximal d'essais de l'exercice est atteint."""


class ValidatorNotAvailable(Exception):
    """Aucun validateur n'existe encore pour ce type d'exercice."""


def submit_exercise(
    user,
    exercise: Exercise,
    submission: Any,
    duration_seconds: int | None = None,
    hints_used: int = 0,
) -> tuple[ExerciseAttempt, Any]:
    """Valide et enregistre une tentative ; renvoie `(tentative, ValidationResult)`."""
    try:
        validator = get_validator(exercise.type)
    except UnsupportedExerciseType as exc:
        raise ValidatorNotAvailable(
            f"La correction des exercices de type {exercise.type} n'est pas "
            "encore disponible."
        ) from exc

    with transaction.atomic():
        # Verrou sur la ligne utilisateur : serialise les soumissions concurrentes
        # meme quand il n'existe encore aucune tentative a verrouiller.
        type(user).objects.select_for_update().filter(pk=user.pk).first()
        previous = list(
            ExerciseAttempt.objects.select_for_update()
            .filter(user=user, exercise=exercise)
            .values_list("attempt_number", flat=True)
        )
        if exercise.max_attempts is not None and len(previous) >= exercise.max_attempts:
            raise MaxAttemptsReached(
                f"Nombre maximal d'essais atteint ({exercise.max_attempts})."
            )
        result = validator.validate(exercise, submission)
        attempt = ExerciseAttempt.objects.create(
            user=user,
            exercise=exercise,
            attempt_number=max(previous, default=0) + 1,
            submission=submission,
            is_correct=result.is_correct,
            score=result.score,
            feedback={"feedback": list(result.feedback), "hints": list(result.hints)},
            hints_used=hints_used,
            duration_seconds=duration_seconds,
        )
        if result.is_correct:
            # Import local : evite un couplage au chargement des apps.
            from apps.gamification.services.xp import award_exercise_xp

            award_exercise_xp(user, exercise)
    return attempt, result


def serialize_result(attempt: ExerciseAttempt, result: Any) -> dict:
    return {**asdict(result), "attempt_number": attempt.attempt_number}
