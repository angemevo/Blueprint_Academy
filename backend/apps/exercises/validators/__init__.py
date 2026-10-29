"""Registre des validateurs de soumission, indexe par type d'exercice.

Un validateur concret se declare avec `@register(ExerciseType.MCQ)` ; le
service de soumission appelle `get_validator(exercise.type).validate(...)`.
Les validateurs concrets sont charges par `ExercisesConfig.ready()`
(`load_validators`) : recall.py pour A, B, C, D ; graph.py pour E, G.
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


def load_validators() -> None:
    """Importe les modules de validateurs concrets (enregistrement par decorateur)."""
    from . import graph, recall  # noqa: F401
