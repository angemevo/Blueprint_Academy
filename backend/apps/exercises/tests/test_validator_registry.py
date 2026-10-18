"""Tests du registre `exercise_type -> Validator`.

Chaque test part d'un registre neuf : le registre par defaut est global et sera
rempli par les validateurs concrets, il ne doit pas etre pollue par les tests.

Ce module fait partie de `apps.exercises` : comme le reste de l'app, il
n'importe `apps.validation` que localement (voir test_validation_isolation).
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


class AlwaysWrong:
    def validate(self, exercise, submission):
        from apps.validation.interfaces import ValidationResult

        return ValidationResult(is_correct=False, score=0)


@pytest.fixture
def registry():
    return ValidatorRegistry()


class TestEnregistrement:
    def test_register_en_decorateur_rend_la_classe_intacte(self, registry):
        decorated = registry.register(ExerciseType.MCQ)(AlwaysCorrect)

        assert decorated is AlwaysCorrect

    def test_get_rend_une_instance_du_validateur_enregistre(self, registry):
        registry.register(ExerciseType.MCQ)(AlwaysCorrect)

        validator = registry.get(ExerciseType.MCQ)

        assert isinstance(validator, AlwaysCorrect)
        assert validator.validate(exercise=None, submission={}).is_correct is True

    def test_get_accepte_la_valeur_brute_du_type(self, registry):
        registry.register(ExerciseType.MCQ)(AlwaysCorrect)

        assert isinstance(registry.get("B"), AlwaysCorrect)

    def test_un_validateur_pour_plusieurs_types(self, registry):
        registry.register(ExerciseType.GRAPH_BUILD, ExerciseType.CHALLENGE)(AlwaysCorrect)

        assert registry.get(ExerciseType.GRAPH_BUILD) is registry.get(ExerciseType.CHALLENGE)

    def test_types_independants(self, registry):
        registry.register(ExerciseType.QUESTION)(AlwaysCorrect)
        registry.register(ExerciseType.MCQ)(AlwaysWrong)

        assert isinstance(registry.get(ExerciseType.QUESTION), AlwaysCorrect)
        assert isinstance(registry.get(ExerciseType.MCQ), AlwaysWrong)

    def test_registered_types(self, registry):
        registry.register(ExerciseType.MCQ, ExerciseType.QUESTION)(AlwaysCorrect)

        assert registry.registered_types() == frozenset(
            {ExerciseType.MCQ, ExerciseType.QUESTION}
        )


class TestRefus:
    def test_type_sans_validateur(self, registry):
        with pytest.raises(UnsupportedExerciseType, match="'B'"):
            registry.get(ExerciseType.MCQ)

    def test_type_inconnu_de_la_taxonomie(self, registry):
        with pytest.raises(UnsupportedExerciseType, match="'Z'"):
            registry.get("Z")

    def test_double_enregistrement_refuse(self, registry):
        registry.register(ExerciseType.MCQ)(AlwaysCorrect)

        with pytest.raises(ValidatorAlreadyRegistered, match="AlwaysCorrect"):
            registry.register(ExerciseType.MCQ)(AlwaysWrong)

        assert isinstance(registry.get(ExerciseType.MCQ), AlwaysCorrect)

    def test_double_enregistrement_partiel_nenregistre_rien(self, registry):
        registry.register(ExerciseType.MCQ)(AlwaysCorrect)

        with pytest.raises(ValidatorAlreadyRegistered):
            registry.register(ExerciseType.QUESTION, ExerciseType.MCQ)(AlwaysWrong)

        with pytest.raises(UnsupportedExerciseType):
            registry.get(ExerciseType.QUESTION)

    def test_enregistrement_sur_type_inconnu_refuse(self, registry):
        with pytest.raises(UnsupportedExerciseType, match="'Z'"):
            registry.register("Z")(AlwaysCorrect)

    def test_enregistrement_sans_type_refuse(self, registry):
        with pytest.raises(ValueError, match="au moins un type"):
            registry.register()

    def test_classe_sans_validate_refusee(self, registry):
        class NotAValidator:
            def check(self, exercise, submission):
                return None

        with pytest.raises(TypeError, match="validate"):
            registry.register(ExerciseType.MCQ)(NotAValidator)

        with pytest.raises(UnsupportedExerciseType):
            registry.get(ExerciseType.MCQ)


def test_fonctions_du_module_branchees_sur_le_registre_par_defaut():
    assert validators.register.__self__ is validators.default_registry
    assert validators.get_validator.__self__ is validators.default_registry
