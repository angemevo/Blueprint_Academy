import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.exercises.models import Exercise, ExerciseAttempt
from apps.gamification.models import XPSource, XPTransaction
from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.progress.models import SkillMastery
from apps.progress.tests.test_lesson_progress import make_client

URL = "/api/progress/dashboard/"


def test_requires_auth(db):
    from rest_framework.test import APIClient

    assert APIClient().get(URL).status_code in (401, 403)


def test_new_user_gets_valid_empty_dashboard(db):
    c, _ = make_client("new")
    r = c.get(URL)
    assert r.status_code == 200
    assert r.data["total_xp"] == 0 and r.data["level"] == 1
    assert r.data["xp_to_next_level"] == 100
    assert r.data["current_paths"] == [] and r.data["next_lesson"] is None
    assert r.data["recent_attempts"] == [] and r.data["skills"] == []


@pytest.fixture
def filled(db):
    base = Skill.objects.create(name="Variables", slug="variables")
    p = LearningPath.objects.create(title="P", slug="p", is_published=True)
    m = Module.objects.create(learning_path=p, title="M", slug="m", is_published=True)
    lessons = [
        Lesson.objects.create(
            module=m, title=f"L{i}", slug=f"l{i}", order=i, is_published=True
        )
        for i in range(3)
    ]
    lessons[0].skills_taught.add(base)
    ex = Exercise.objects.create(
        lesson=lessons[0], type="A", title="Q", slug="q",
        content={"question": "Q ?"}, solution={"accepted_answers": ["zebra42"]}, is_published=True,
    )
    return p, lessons, base, ex


def test_values_match_ledger_and_attempts(filled):
    p, lessons, base, ex = filled
    c, u = make_client("a")
    for i, amt in enumerate((60, 90)):
        XPTransaction.objects.create(
            user=u, amount=amt, source=XPSource.EXERCISE_SOLVED, reference_key=f"k{i}"
        )
    for n in range(1, 8):
        ExerciseAttempt.objects.create(
            user=u, exercise=ex, attempt_number=n, is_correct=n == 7, score=n
        )
    SkillMastery.objects.create(user=u, skill=base, mastery_score=80)
    assert c.post(f"/api/lessons/{lessons[0].id}/complete/").status_code == 200
    r = c.get(URL).data
    assert r["total_xp"] == 150 and r["level"] == 2
    assert r["next_level_xp"] == 250 and r["xp_to_next_level"] == 100
    assert [a["attempt_number"] for a in r["recent_attempts"]] == [7, 6, 5, 4, 3]
    assert r["current_paths"][0]["completion_percent"] == 33
    assert r["next_lesson"]["id"] == lessons[1].id
    assert r["skills"] == [
        {"id": base.id, "name": "Variables", "mastery_score": 80, "is_mastered": True}
    ]
    assert "zebra42" not in str(r) and "solution" not in str(r)


def test_query_count_bounded(filled):
    p, lessons, base, ex = filled
    c, u = make_client("q")
    c.post(f"/api/lessons/{lessons[0].id}/start/")
    for n in range(1, 6):
        ExerciseAttempt.objects.create(user=u, exercise=ex, attempt_number=n)
    with CaptureQueriesContext(connection) as small:
        c.get(URL)
    for i in range(10):
        s = Skill.objects.create(name=f"S{i}", slug=f"s{i}")
        SkillMastery.objects.create(user=u, skill=s, mastery_score=i)
        Lesson.objects.create(
            module=lessons[0].module, title=f"X{i}", slug=f"x{i}", order=10 + i,
            is_published=True,
        ).required_skills.add(s)
    with CaptureQueriesContext(connection) as big:
        c.get(URL)
    assert len(big) == len(small) <= 10


def test_read_only_and_per_user(filled):
    p, lessons, base, ex = filled
    c, u = make_client("o")
    other, ou = make_client("p")
    ExerciseAttempt.objects.create(user=ou, exercise=ex, attempt_number=1)
    SkillMastery.objects.create(user=ou, skill=base, mastery_score=50)
    r = c.get(URL).data
    assert r["recent_attempts"] == [] and r["skills"] == []
    assert c.post(URL).status_code == 405
