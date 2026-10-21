"""Tests des interfaces de l'app validation (aucun acces base)."""

import pytest

from apps.validation.interfaces import MAX_SCORE, MIN_SCORE, ValidationResult, Validator


def test_construction_et_valeurs_par_defaut():
    result = ValidationResult(is_correct=False, score=40, hints=["Relie BeginPlay."])

    assert (result.is_correct, result.score) == (False, 40)
    assert result.feedback == []
    assert result.hints == ["Relie BeginPlay."]
    result.feedback.append("x")  # les listes par defaut ne sont pas partagees
    assert ValidationResult(is_correct=True, score=100).feedback == []


@pytest.mark.parametrize("score", [MIN_SCORE, 50, MAX_SCORE])
def test_score_dans_les_bornes_accepte(score):
    assert ValidationResult(is_correct=False, score=score).score == score


@pytest.mark.parametrize("score", [-1, MAX_SCORE + 1])
def test_score_hors_bornes_refuse(score):
    with pytest.raises(ValueError, match="score"):
        ValidationResult(is_correct=False, score=score)


@pytest.mark.parametrize("score", [50.0, "50", None, True])
def test_score_non_entier_refuse(score):
    with pytest.raises(TypeError, match="score"):
        ValidationResult(is_correct=False, score=score)


def test_resultat_immuable():
    with pytest.raises(AttributeError):
        ValidationResult(is_correct=True, score=100).score = 0


def test_validator_reconnu_par_sa_forme():
    class FakeValidator:
        def validate(self, exercise, submission):
            return ValidationResult(is_correct=True, score=100)

    class NotAValidator:
        def check(self, exercise, submission):
            return None

    assert isinstance(FakeValidator(), Validator)
    assert not isinstance(NotAValidator(), Validator)
