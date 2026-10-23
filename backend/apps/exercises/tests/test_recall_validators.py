"""Validateurs A, B, C, D : juste, faux, partiel, mal forme, et feedback sans fuite."""

from types import SimpleNamespace

import pytest

from apps.exercises.validators import get_validator


def ex(type_, content, solution):
    return SimpleNamespace(type=type_, content=content, solution=solution)


def run(exercise, submission):
    return get_validator(exercise.type).validate(exercise, submission)


QUESTION = ex("A", {"question": "?"}, {"accepted_answers": ["Begin Play", "BeginPlay"]})
MCQ = ex(
    "B",
    {"options": [{"id": "o1", "text": "x"}, {"id": "o2", "text": "y"}, {"id": "o3", "text": "z"}]},
    {"correct_option_ids": ["o1", "o3"], "option_explanations": {"o2": "Pas celui-ci."}},
)
ORDERING = ex(
    "C",
    {"items": [{"id": i, "label": i} for i in ("a", "b", "c", "d")]},
    {"order": ["a", "b", "c", "d"]},
)
MATCHING = ex(
    "D",
    {
        "left": [{"id": "l1", "label": "x"}, {"id": "l2", "label": "y"}],
        "right": [{"id": "r1", "label": "x"}, {"id": "r2", "label": "y"}],
    },
    {"pairs": [{"left_id": "l1", "right_id": "r1"}, {"left_id": "l2", "right_id": "r2"}]},
)


def pairs(*items):
    return {"pairs": [{"left_id": a, "right_id": b} for a, b in items]}


@pytest.mark.parametrize("answer", ["BeginPlay", "  begin   PLAY ", "beginplay"])
def test_question_juste(answer):
    result = run(QUESTION, {"answer": answer})
    assert result.is_correct and result.score == 100


def test_question_casse_respectee_si_demandee():
    exercise = ex("A", {}, {"accepted_answers": ["BeginPlay"], "case_sensitive": True})
    assert not run(exercise, {"answer": "beginplay"}).is_correct
    assert run(exercise, {"answer": " BeginPlay"}).is_correct


def test_question_fausse():
    result = run(QUESTION, {"answer": "Tick"})
    assert (result.is_correct, result.score) == (False, 0)


@pytest.mark.parametrize("submission", [None, {}, {"answer": 3}, {"answer": "  "}, "x"])
def test_question_mal_formee(submission):
    result = run(QUESTION, submission)
    assert (result.is_correct, result.score) == (False, 0) and result.feedback


def test_qcm_juste_quel_que_soit_lordre():
    assert run(MCQ, {"selected_option_ids": ["o3", "o1"]}).is_correct


@pytest.mark.parametrize("selected", [["o1"], ["o1", "o2", "o3"], ["o2"]])
def test_qcm_faux_ou_partiel_vaut_zero(selected):
    result = run(MCQ, {"selected_option_ids": selected})
    assert (result.is_correct, result.score) == (False, 0)


def test_qcm_explication_de_loption_cochee():
    assert "Pas celui-ci." in run(MCQ, {"selected_option_ids": ["o2"]}).feedback


@pytest.mark.parametrize(
    "submission",
    [None, {}, {"selected_option_ids": []}, {"selected_option_ids": "o1"},
     {"selected_option_ids": ["zz"]}, {"selected_option_ids": ["o1", "o1"]}],
)
def test_qcm_mal_forme(submission):
    result = run(MCQ, submission)
    assert (result.is_correct, result.score) == (False, 0) and result.feedback


def test_ordre_juste():
    result = run(ORDERING, {"order": ["a", "b", "c", "d"]})
    assert result.is_correct and result.score == 100


def test_ordre_partiel():
    result = run(ORDERING, {"order": ["a", "b", "d", "c"]})
    assert (result.is_correct, result.score) == (False, 50)


def test_ordre_faux():
    assert run(ORDERING, {"order": ["d", "c", "b", "a"]}).score == 0


@pytest.mark.parametrize(
    "submission",
    [None, {}, {"order": ["a", "b"]}, {"order": ["a", "a", "b", "c"]}, {"order": ["a", "b", "c", "x"]}],
)
def test_ordre_mal_forme(submission):
    result = run(ORDERING, submission)
    assert (result.is_correct, result.score) == (False, 0) and result.feedback


def test_matching_juste():
    result = run(MATCHING, pairs(("l2", "r2"), ("l1", "r1")))
    assert result.is_correct and result.score == 100


def test_matching_partiel():
    result = run(MATCHING, pairs(("l1", "r1")))
    assert (result.is_correct, result.score) == (False, 50)


def test_matching_croise_et_surplus():
    assert run(MATCHING, pairs(("l1", "r2"), ("l2", "r1"))).score == 0
    surplus = run(MATCHING, pairs(("l1", "r1"), ("l2", "r2"), ("l1", "r2")))
    assert not surplus.is_correct and surplus.score < 100


@pytest.mark.parametrize(
    "submission",
    [None, {}, {"pairs": []}, {"pairs": ["x"]}, pairs(("zz", "r1")), pairs(("l1", "zz"))],
)
def test_matching_mal_forme(submission):
    result = run(MATCHING, submission)
    assert (result.is_correct, result.score) == (False, 0) and result.feedback


def test_feedback_ne_revele_aucune_reponse_attendue():
    secrets = ["BeginPlay", "Begin Play", "o1", "o3", "l1", "r1", "r2"]
    cases = [
        (QUESTION, {"answer": "Tick"}),
        (QUESTION, {}),
        (MCQ, {"selected_option_ids": ["o2"]}),
        (MCQ, {"selected_option_ids": ["o1"]}),
        (ORDERING, {"order": ["a", "b", "d", "c"]}),
        (ORDERING, {"order": ["a"]}),
        (MATCHING, pairs(("l1", "r2"))),
        (MATCHING, pairs(("zz", "r1"))),
    ]
    for exercise, submission in cases:
        text = " ".join(run(exercise, submission).feedback)
        for secret in secrets:
            assert secret not in text, (exercise.type, secret)
