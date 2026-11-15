"""Parcours etudiant de bout en bout, par l'API uniquement (issue #71).

Les donnees sont creees ici (pas par `seed_blueprint`). Types A, B, C, D.
"""
import json

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.exercises.models import Exercise, ExerciseAttempt
from apps.gamification.models import XPSource, XPTransaction
from apps.gamification.services.xp import level_for_xp
from apps.learning.models import LearningPath, Lesson, Module
from apps.users.models import Profile

PW = "Zx9!longpassword42"
SECRET = "SECRET-SOLUTION-MARKER"
XP = {"A": 60, "B": 60, "C": 15, "D": 5}

PAIRS_OK = [{"left_id": "l1", "right_id": "r1"}, {"left_id": "l2", "right_id": "r2"}]
PAIRS_KO = [{"left_id": "l1", "right_id": "r2"}, {"left_id": "l2", "right_id": "r1"}]

# type -> (content, solution, bonne soumission, mauvaise soumission)
SPECS = {
    "A": (
        {"question": "Q ?"},
        {"accepted_answers": ["zebra42"], "explanation": SECRET},
        {"answer": "zebra42"},
        {"answer": "faux"},
    ),
    "B": (
        {"question": "Q", "options": [{"id": "o1", "text": "x"}, {"id": "o2", "text": "y"}]},
        {"correct_option_ids": ["o1"], "explanation": SECRET},
        {"selected_option_ids": ["o1"]},
        {"selected_option_ids": ["o2"]},
    ),
    "C": (
        {"items": [{"id": f"i{k}", "label": f"L{k}"} for k in range(4)]},
        {"order": [f"i{k}" for k in range(4)], "explanation": SECRET},
        {"order": ["i0", "i1", "i2", "i3"]},
        {"order": ["i3", "i2", "i1", "i0"]},
    ),
    "D": (
        {
            "left": [{"id": "l1", "label": "a"}, {"id": "l2", "label": "b"}],
            "right": [{"id": "r1", "label": "c"}, {"id": "r2", "label": "d"}],
        },
        {"pairs": PAIRS_OK, "explanation": SECRET},
        {"pairs": PAIRS_OK},
        {"pairs": PAIRS_KO},
    ),
}


@pytest.fixture
def world(db, settings):
    settings.EXERCISE_XP_DEFAULTS = {**settings.EXERCISE_XP_DEFAULTS, **XP}
    path = LearningPath.objects.create(title="P", slug="p", is_published=True)
    LearningPath.objects.create(title="Brouillon", slug="brouillon", is_published=False)
    mod = Module.objects.create(learning_path=path, title="M", slug="m", is_published=True)
    lesson = Lesson.objects.create(module=mod, title="L", slug="l", is_published=True)
    exercises = {
        t: Exercise.objects.create(
            lesson=lesson, type=t, title=f"E{t}", slug=f"e-{t.lower()}",
            content=spec[0], solution=spec[1], is_published=True,
        )
        for t, spec in SPECS.items()
    }
    return lesson, exercises


def register_and_login():
    c = APIClient()
    r = c.post(
        "/api/auth/register/",
        {"username": "eve", "email": "eve@example.com", "password": PW},
    )
    assert r.status_code == 201
    r = c.post("/api/auth/login/", {"username": "eve", "password": PW})
    assert r.status_code == 200
    c.credentials(HTTP_AUTHORIZATION="Bearer " + r.json()["access"])
    return c


def submit(c, ex, payload):
    r = c.post(f"/api/exercises/{ex.pk}/submit/", {"submission": payload}, format="json")
    assert r.status_code == 200
    return r.json()


def solved_count(ex):
    return XPTransaction.objects.filter(
        user__username="eve",
        source=XPSource.EXERCISE_SOLVED,
        reference_key=f"exercise:{ex.pk}",
    ).count()


def test_student_journey(world):
    lesson, exercises = world
    c = register_and_login()

    # Catalogue : seul le parcours publie est visible.
    r = c.get("/api/learning-paths/")
    assert r.status_code == 200
    assert [p["slug"] for p in r.json()["results"]] == ["p"]
    assert c.get("/api/learning-paths/brouillon/").status_code == 404
    detail = c.get("/api/learning-paths/p/")
    assert detail.status_code == 200
    assert detail.json()["modules"][0]["lessons"][0]["id"] == lesson.pk

    # Lecon : liste des exercices, sans contenu ni solution.
    r = c.get(f"/api/lessons/{lesson.pk}/")
    assert r.status_code == 200
    assert {e["type"] for e in r.json()["exercises"]} == set(SPECS)
    assert SECRET not in json.dumps(r.json())

    total = 0
    for t, ex in exercises.items():
        good, bad = SPECS[t][2], SPECS[t][3]
        r = c.get(f"/api/exercises/{ex.pk}/")
        assert r.status_code == 200
        raw = json.dumps(r.json())
        assert "solution" not in r.json()
        assert SECRET not in raw and "zebra42" not in raw

        wrong = submit(c, ex, bad)
        assert wrong["is_correct"] is False and wrong["attempt_number"] == 1
        assert solved_count(ex) == 0

        right = submit(c, ex, good)
        assert right["is_correct"] is True and right["attempt_number"] == 2
        total += XP[t]
        assert solved_count(ex) == 1

        # Rejouer une bonne reponse : tentative 3, mais pas de nouvel XP.
        assert submit(c, ex, good)["attempt_number"] == 3
        assert solved_count(ex) == 1

    assert ExerciseAttempt.objects.filter(user__username="eve").count() == 3 * len(SPECS)

    # Tableau de bord coherent avec le ledger et la courbe de niveaux.
    r = c.get("/api/progress/dashboard/")
    assert r.status_code == 200
    d = r.json()
    assert d["total_xp"] == total == Profile.objects.get(user__username="eve").total_xp
    assert d["level"] == level_for_xp(total) == 2
    thresholds = settings.XP_LEVEL_THRESHOLDS
    assert thresholds[d["level"] - 1] <= total < thresholds[d["level"]]
    assert d["xp_to_next_level"] == thresholds[d["level"]] - total
    assert len(d["recent_attempts"]) > 0


def test_anonymous_cannot_read_exercise_or_dashboard(world):
    _lesson, exercises = world
    c = APIClient()
    assert c.get(f"/api/exercises/{exercises['A'].pk}/").status_code in (401, 403)
    assert c.get("/api/progress/dashboard/").status_code in (401, 403)
