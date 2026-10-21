"""Registre des validateurs de soumission, indexe par type d'exercice.

Un validateur concret se declare avec `@register(ExerciseType.MCQ)` ; le
service de soumission appelle `get_validator(exercise.type).validate(...)`.
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
