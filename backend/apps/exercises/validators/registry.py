"""Registre `exercise_type -> Validator`.

Les cles sont les valeurs de `ExerciseType` (`apps/exercises/enums.py`), seule
source de la taxonomie : le registre ne declare aucune liste de types, il
refuse simplement ce que l'enum ne connait pas.

Les contrats (`Validator`, `ValidationResult`) vivent dans `apps.validation`,
app isolee : ils ne sont importes que LOCALEMENT, a l'interieur des fonctions
(CLAUDE.md, « Architecture backend »).
"""

from collections.abc import Callable
from typing import Any

from ..enums import ExerciseType


class UnsupportedExerciseType(LookupError):
    """Aucun validateur pour ce type, ou type absent de la taxonomie."""


class ValidatorAlreadyRegistered(ValueError):
    """Un type d'exercice a deja son validateur."""


def _as_exercise_type(exercise_type: str) -> ExerciseType:
    try:
        return ExerciseType(exercise_type)
    except ValueError as exc:
        raise UnsupportedExerciseType(
            f"Type d'exercice inconnu de la taxonomie : {exercise_type!r}."
        ) from exc


class ValidatorRegistry:
    """Associe a chaque type d'exercice une instance unique de validateur."""

    def __init__(self) -> None:
        # Annote en `Any` : nommer `Validator` ici obligerait a importer
        # `apps.validation` au niveau module.
        self._validators: dict[ExerciseType, Any] = {}

    def register(self, *exercise_types: str) -> Callable[[type], type]:
        """Decorateur : `@register(ExerciseType.MCQ)` sur une classe de validateur.

        Un meme validateur peut servir plusieurs types. L'enregistrement est
        atomique : si l'un des types est inconnu ou deja pris, aucun n'est
        enregistre.
        """
        if not exercise_types:
            raise ValueError("register() attend au moins un type d'exercice.")
        types = [_as_exercise_type(exercise_type) for exercise_type in exercise_types]

        def decorator(validator_class: type) -> type:
            from apps.validation.interfaces import Validator

            instance = validator_class()
            if not isinstance(instance, Validator):
                raise TypeError(
                    f"{validator_class.__name__} doit definir "
                    "validate(exercise, submission) -> ValidationResult."
                )
            for exercise_type in types:
                if exercise_type in self._validators:
                    current = type(self._validators[exercise_type]).__name__
                    raise ValidatorAlreadyRegistered(
                        f"Le type {exercise_type.value!r} a deja un validateur "
                        f"({current}) ; {validator_class.__name__} est refuse."
                    )
            for exercise_type in types:
                self._validators[exercise_type] = instance
            return validator_class

        return decorator

    def get(self, exercise_type: str) -> Any:
        """Validateur du type, ou `UnsupportedExerciseType`."""
        key = _as_exercise_type(exercise_type)
        try:
            return self._validators[key]
        except KeyError as exc:
            raise UnsupportedExerciseType(
                f"Aucun validateur enregistre pour le type {key.value!r} ({key.label})."
            ) from exc

    def registered_types(self) -> frozenset[ExerciseType]:
        return frozenset(self._validators)


#: Registre de la plateforme, rempli par les validateurs concrets a leur import.
default_registry = ValidatorRegistry()
