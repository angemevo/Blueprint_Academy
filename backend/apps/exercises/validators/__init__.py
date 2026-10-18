"""Registre des validateurs de soumission, indexe par type d'exercice.

Usage, pour un validateur concret :

    from apps.exercises.enums import ExerciseType
    from apps.exercises.validators import register

    @register(ExerciseType.MCQ)
    class McqValidator:
        def validate(self, exercise, submission):
            from apps.validation.interfaces import ValidationResult
            ...

puis, cote service de soumission : `get_validator(exercise.type).validate(...)`.

Les validateurs concrets arrivent dans les issues suivantes.
"""

from .registry import (
    UnsupportedExerciseType,
    ValidatorAlreadyRegistered,
    ValidatorRegistry,
    default_registry,
)

register = default_registry.register
get_validator = default_registry.get

__all__ = [
    "UnsupportedExerciseType",
    "ValidatorAlreadyRegistered",
    "ValidatorRegistry",
    "default_registry",
    "get_validator",
    "register",
]
