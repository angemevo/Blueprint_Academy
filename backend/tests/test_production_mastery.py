"""Production, maitrise et verrouillage de bout en bout (issue #72).

Reutilise les outils de `test_student_journey` (inscription, soumission).
Les graphes sont synthetiques : a verifier dans Unreal avant tout usage
pedagogique reel.
"""
import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.exercises.models import Exercise, ExerciseAttempt
from apps.exercises.tests.test_exercise_api import BEGIN, PRINT, SPECS
from apps.gamification.models import XPSource, XPTransaction
from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.learning.services.publication import publish
from apps.progress.models import SkillMastery
from apps.users.models import User
from tests.test_student_journey import SPECS as RECALL_SPECS
from tests.test_student_journey import register_and_login, submit

RECALL_GOOD = {t: spec[2] for t, spec in RECALL_SPECS.items()}

# A verifier dans Unreal : graphes synthetiques, pas des exports reels.
GOOD = {"nodes": [{"id": "p", "type": PRINT}], "edges": []}
BAD = {"nodes": [{"id": "b", "type": BEGIN}], "edges": []}


@pytest.fixture
def world(db, settings):
    settings.EXERCISE_XP_DEFAULTS = {**settings.EXERCISE_XP_DEFAULTS, "H": 35, "E": 50}
    skill = Skill.objects.create(name="Variables", slug="variables")
    path = LearningPath.objects.create(title="P", slug="p", is_published=True)
    mod = Module.objects.create(learning_path=path, title="M", slug="m", is_published=True)
    lesson = Lesson.objects.create(module=mod, title="L", slug="l", is_published=True)
    lesson.skills_taught.add(skill)
    exercises = {}
    for t in "ABCDEFGH":
        content, solution = (RECALL_SPECS if t in RECALL_SPECS else SPECS)[t][:2]
        e = Exercise.objects.create(
            lesson=lesson, type=t, title=f"E{t}", slug=f"e-{t.lower()}",
            content=content, solution=solution, is_published=True,
        )
        e.skills.add(skill)
        exercises[t] = e
    return skill, lesson, exercises


def mastery(skill):
    return SkillMastery.objects.get(user__username="eve", skill=skill)


def xp_of(ex):
    return list(
        XPTransaction.objects.filter(
            user__username="eve", source=XPSource.EXERCISE_SOLVED,
            reference_key=f"exercise:{ex.pk}",
        ).values_list("amount", flat=True)
    )


def test_production_wrong_then_right_moves_mastery(world):
    skill, _lesson, ex = world
    c = register_and_login()

    wrong = submit(c, ex["H"], BAD)
    assert wrong["is_correct"] is False and wrong["attempt_number"] == 1
    assert xp_of(ex["H"]) == []
    assert not SkillMastery.objects.filter(user__username="eve", skill=skill, mastery_score__gt=0)

    right = submit(c, ex["H"], GOOD)
    assert right["is_correct"] is True and right["attempt_number"] == 2
    assert xp_of(ex["H"]) == [35]
    after_h = mastery(skill)
    assert after_h.successes_count == 1 and after_h.attempts_count == 2
    assert 0 < after_h.mastery_score < 100 and not after_h.is_mastered

    # Exercice de construction libre (E) : la maitrise progresse encore.
    assert submit(c, ex["E"], BAD)["is_correct"] is False
    assert submit(c, ex["E"], GOOD)["attempt_number"] == 2
    assert xp_of(ex["E"]) == [50]
    assert mastery(skill).mastery_score > after_h.mastery_score
    assert ExerciseAttempt.objects.filter(user__username="eve").count() == 4

    d = c.get("/api/progress/dashboard/").json()
    assert d["total_xp"] == 85
    assert d["skills"][0]["mastery_score"] == mastery(skill).mastery_score


def test_mastery_reaches_100_with_production_only(world):
    skill, _lesson, ex = world
    other = User.objects.create_user(username="slow", password="x")
    for t in "EFGH":
        ExerciseAttempt.objects.create(
            user=other, exercise=ex[t], is_correct=True, duration_seconds=1000
        )
    c = register_and_login()
    for t in "EFGH":  # sans type I, reussite du premier coup et plus vite que la moyenne
        r = c.post(
            f"/api/exercises/{ex[t].pk}/submit/",
            {"submission": GOOD, "duration_seconds": 5},
            format="json",
        )
        assert r.status_code == 200 and r.json()["is_correct"] is True
    m = mastery(skill)
    assert m.mastery_score == 100 and m.is_mastered
    assert not ExerciseAttempt.objects.filter(user__username="eve", exercise__type="I").exists()


def test_recall_exercises_never_move_mastery(world):
    _skill, _lesson, ex = world
    c = register_and_login()
    for t in "ABCD":
        good = RECALL_GOOD[t]
        assert submit(c, ex[t], good)["is_correct"] is True
    assert ExerciseAttempt.objects.filter(user__username="eve", is_correct=True).count() == 4
    assert not SkillMastery.objects.exists()


def test_lesson_locked_until_prerequisite_skill_mastered(world):
    skill, _lesson, ex = world
    path = LearningPath.objects.get(slug="p")
    mod = Module.objects.get(slug="m")
    nxt = Lesson.objects.create(module=mod, title="Suite", slug="suite", order=9, is_published=True)
    nxt.required_skills.add(skill)
    assert path.is_published

    other = User.objects.create_user(username="slow", password="x")
    for t in "EFGH":
        ExerciseAttempt.objects.create(
            user=other, exercise=ex[t], is_correct=True, duration_seconds=1000
        )
    c = register_and_login()
    r = c.post(f"/api/lessons/{nxt.pk}/start/")
    assert r.status_code == 403
    assert [s["name"] for s in r.json()["missing_skills"]] == ["Variables"]

    # Un seul exercice reussi ne suffit pas.
    c.post(f"/api/exercises/{ex['H'].pk}/submit/", {"submission": GOOD, "duration_seconds": 5}, format="json")
    assert c.post(f"/api/lessons/{nxt.pk}/start/").status_code == 403

    for t in "EFG":
        c.post(f"/api/exercises/{ex[t].pk}/submit/", {"submission": GOOD, "duration_seconds": 5}, format="json")
    assert mastery(skill).is_mastered
    assert c.post(f"/api/lessons/{nxt.pk}/start/").status_code == 200
    assert APIClient().post(f"/api/lessons/{nxt.pk}/start/").status_code in (401, 403)


def test_path_failing_integrity_cannot_be_published(db):
    skill = Skill.objects.create(name="Pauvre", slug="pauvre")
    path = LearningPath.objects.create(title="P", slug="p")
    mod = Module.objects.create(learning_path=path, title="M", slug="m")
    lesson = Lesson.objects.create(module=mod, title="L", slug="l")
    lesson.skills_taught.add(skill)
    content, solution = SPECS["E"]
    Exercise.objects.create(
        lesson=lesson, type="E", title="E", slug="e", content=content,
        solution=solution, is_published=True,
    ).skills.add(skill)

    assert publish(path) != []
    path.refresh_from_db()
    assert path.is_published is False
    path.is_published = True
    with pytest.raises(ValidationError):
        path.save()
    assert not LearningPath.objects.get(pk=path.pk).is_published

    # Avec assez d'exercices de production (dont un contraint), la publication passe.
    for n, t in enumerate("GH"):
        c2, s2 = SPECS[t]
        Exercise.objects.create(
            lesson=lesson, type=t, title=t, slug=f"x{n}", content=c2,
            solution=s2, is_published=True,
        ).skills.add(skill)
    assert publish(path) == []
    assert LearningPath.objects.get(pk=path.pk).is_published
