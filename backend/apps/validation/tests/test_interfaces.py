"""Tests des interfaces de l'app validation : resultat et protocoles.

Aucun acces base : l'app validation ne declare ni modele ni requete.
"""

import pytest

from apps.validation.interfaces import (
    MAX_SCORE,
    MIN_SCORE,
    HintService,
    ValidationResult,
    Validator,
)


class TestValidationResult:
    def test_construction_complete(self):
        result = ValidationResult(
            is_correct=False,
            score=40,
            feedback=["Le node Print String n'est pas relie a BeginPlay."],
            hints=["Tire un fil depuis le pin d'execution de BeginPlay."],
        )

        assert result.is_correct is False
        assert result.score == 40
        assert result.feedback == ["Le node Print String n'est pas relie a BeginPlay."]
        assert result.hints == ["Tire un fil depuis le pin d'execution de BeginPlay."]

    def test_feedback_et_indices_vides_par_defaut(self):
        result = ValidationResult(is_correct=True, score=100)

        assert result.feedback == []
        assert result.hints == []

    def test_listes_par_defaut_non_partagees(self):
        first = ValidationResult(is_correct=True, score=100)
        second = ValidationResult(is_correct=True, score=100)

        first.feedback.append("bravo")

        assert second.feedback == []

    @pytest.mark.parametrize("score", [MIN_SCORE, 1, 50, 99, MAX_SCORE])
    def test_score_dans_les_bornes_accepte(self, score):
        assert ValidationResult(is_correct=False, score=score).score == score

    @pytest.mark.parametrize("score", [-1, MAX_SCORE + 1, 1000])
    def test_score_hors_bornes_refuse(self, score):
        with pytest.raises(ValueError, match="score"):
            ValidationResult(is_correct=False, score=score)

    @pytest.mark.parametrize("score", [50.0, "50", None, True])
    def test_score_non_entier_refuse(self, score):
        with pytest.raises(TypeError, match="score"):
            ValidationResult(is_correct=False, score=score)

    def test_immuable(self):
        result = ValidationResult(is_correct=True, score=100)

        with pytest.raises(AttributeError):
            result.score = 0


class TestProtocoles:
    def test_validator_reconnu_par_sa_forme(self):
        class FakeValidator:
            def validate(self, exercise, submission):
                return ValidationResult(is_correct=True, score=100)

        assert isinstance(FakeValidator(), Validator)

    def test_objet_sans_validate_nest_pas_un_validator(self):
        class NotAValidator:
            def check(self, exercise, submission):
                return None

        assert not isinstance(NotAValidator(), Validator)

    def test_hint_service_declare_sans_implementation(self):
        assert hasattr(HintService, "next_hint")
