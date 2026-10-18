"""Tests du registre, chacun sur un registre neuf pour ne pas polluer celui par defaut.

Comme tout `apps.exercises`, ce module n'importe `apps.validation` que localement.
"""

import pytest

from apps.exercises import validators
from apps.exercises.enums import ExerciseType
from apps.exercises.validators import (
    UnsupportedExerciseType,
    ValidatorAlreadyRegistered,
    ValidatorRegistry,
)


class AlwaysCorrect:
    def validate(self, exercise, submission):
        from apps.validation.interfaces import ValidationResult

        return ValidationResult(is_correct=True, score=100)


class OtherValidator(AlwaysCorrect):
    pass


@pytest.fixture
def registry():
    return ValidatorRegistry()


def test_register_en_decorateur_puis_recuperation(registry):
    assert registry.register(ExerciseType.MCQ)(AlwaysCorrect) is AlwaysCorrect

    validator = registry.get(ExerciseType.MCQ)

    assert isinstance(validator, AlwaysCorrect)
    assert validator.validate(exercise=None, submission={}).is_correct is True
    assert registry.get("B") is validator  # valeur brute de l'enum


def test_un_validateur_pour_plusieurs_types(registry):
    registry.register(ExerciseType.GRAPH_BUILD, ExerciseType.CHALLENGE)(AlwaysCorrect)

    assert registry.get(ExerciseType.GRAPH_BUILD) is registry.get(ExerciseType.CHALLENGE)


@pytest.mark.parametrize(
    ("exercise_type", "message"),
    [(ExerciseType.MCQ, "Aucun validateur.*'B'"), ("Z", "inconnu.*'Z'")],
)
def test_type_sans_validateur_ou_inconnu(registry, exercise_type, message):
    with pytest.raises(UnsupportedExerciseType, match=message):
        registry.get(exercise_type)


def test_double_enregistrement_refuse_et_atomique(registry):
    registry.register(ExerciseType.MCQ)(AlwaysCorrect)

    with pytest.raises(ValidatorAlreadyRegistered, match="AlwaysCorrect"):
        registry.register(ExerciseType.QUESTION, ExerciseType.MCQ)(OtherValidator)

    assert type(registry.get(ExerciseType.MCQ)) is AlwaysCorrect
    with pytest.raises(UnsupportedExerciseType):  # QUESTION non enregistre non plus
        registry.get(ExerciseType.QUESTION)


def test_enregistrements_invalides_refuses(registry):
    class NotAValidator:
        def check(self, exercise, submission):
            return None

    with pytest.raises(UnsupportedExerciseType, match="'Z'"):
        registry.register("Z")
    with pytest.raises(ValueError, match="au moins un type"):
        registry.register()
    with pytest.raises(TypeError, match="validate"):
        registry.register(ExerciseType.MCQ)(NotAValidator)
    with pytest.raises(UnsupportedExerciseType):
        registry.get(ExerciseType.MCQ)


def test_fonctions_du_module_branchees_sur_le_registre_par_defaut():
    assert validators.register.__self__ is validators.default_registry
    assert validators.get_validator.__self__ is validators.default_registry
