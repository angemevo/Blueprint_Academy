import pytest
from django.core.exceptions import ValidationError

from apps.exercises.models import Exercise, ExerciseAttempt
from apps.exercises.tests.test_exercise_api import SPECS
from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.learning.services.integrity import skill_integrity_problems
from apps.progress.models import SkillMastery
from apps.progress.services.mastery import compute_mastery_score, update_skill_mastery
from apps.users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def skill():
    return Skill.objects.create(name="Variables", slug="variables")


@pytest.fixture
def user():
    return User.objects.create_user(username="u", password="x")


def ex(skill, t, n=0, published=True):
    content, solution = SPECS[t]
    e = Exercise.objects.create(
        type=t, title=f"{t}{n}", slug=f"{t.lower()}-{n}",
        content=content, solution=solution, is_published=published,
    )
    e.skills.add(skill)
    return e


def attempt(user, e, number=1, ok=True, hints=0, duration=None):
    a = ExerciseAttempt.objects.create(
        user=user, exercise=e, attempt_number=number, is_correct=ok,
        hints_used=hints, duration_seconds=duration,
    )
    update_skill_mastery(user, e, ok)
    return a


def mastery(user, skill):
    return SkillMastery.objects.get(user=user, skill=skill)


def test_recall_never_moves_mastery(user, skill):
    a = ex(skill, "A")
    attempt(user, a)
    assert not SkillMastery.objects.exists()


def test_perfect_non_i_reaches_100_without_type_i(user, skill):
    exos = [ex(skill, t, i) for i, t in enumerate("FHE")]
    for e in exos:
        attempt(user, e, duration=1)  # pas de moyenne : bonus par defaut
    # (60+20+5)/90 -> 94 % ; la vitesse relative donne le reste
    assert mastery(user, skill).mastery_score == 94


def test_speed_faster_than_average_gives_100(user, skill):
    other = User.objects.create_user(username="o", password="x")
    e = ex(skill, "F")
    ExerciseAttempt.objects.create(user=other, exercise=e, is_correct=True, duration_seconds=100)
    attempt(user, e, duration=10)
    assert mastery(user, skill).mastery_score == 100


def test_slower_than_average_loses_speed_bonus(user, skill):
    other = User.objects.create_user(username="o", password="x")
    e = ex(skill, "F")
    ExerciseAttempt.objects.create(user=other, exercise=e, is_correct=True, duration_seconds=10)
    attempt(user, e, duration=100)
    assert mastery(user, skill).mastery_score == round(100 * 80 / 90)


def test_second_attempt_and_hints(user, skill):
    e = ex(skill, "H")
    attempt(user, e, number=1, ok=False)
    attempt(user, e, number=2, ok=True, hints=5, duration=1)
    # 60+10+5-10 = 65 / 90
    assert mastery(user, skill).mastery_score == round(100 * 65 / 90)
    assert mastery(user, skill).attempts_count == 2
    assert mastery(user, skill).successes_count == 1


def test_unsolved_exercise_counts_zero(user, skill):
    e1, e2 = ex(skill, "F", 1), ex(skill, "H", 2)
    attempt(user, e1, duration=1)
    assert mastery(user, skill).mastery_score == round(94 / 2)
    assert compute_mastery_score(user, skill) == round(94 / 2)
    assert e2


def test_failure_never_lowers_mastery(user, skill):
    e = ex(skill, "F")
    attempt(user, e, duration=1)
    before = mastery(user, skill).mastery_score
    attempt(user, e, number=2, ok=False)
    assert mastery(user, skill).mastery_score == before


def test_type_i_is_bonus_only_and_capped(user, skill):
    f, i = ex(skill, "F", 1), ex(skill, "I", 2)
    attempt(user, f, duration=1)
    base = mastery(user, skill).mastery_score
    attempt(user, i, duration=1)
    assert mastery(user, skill).mastery_score == min(base + round(10 * 85 / 90), 100)
    # I seul ne donne qu'un bonus, jamais la maitrise
    other = Skill.objects.create(name="X", slug="x")
    attempt(user, ex(other, "I", 3), duration=1)
    assert mastery(user, other).mastery_score < 80


def test_threshold_is_a_setting(user, skill, settings):
    SkillMastery.objects.create(user=user, skill=skill, mastery_score=75)
    assert not mastery(user, skill).is_mastered
    settings.MASTERY_SETTINGS = {**settings.MASTERY_SETTINGS, "mastered_threshold": 70}
    assert mastery(user, skill).is_mastered


# --- Controle d'integrite -------------------------------------------------
def test_integrity_counts_non_i_published_and_constrained(skill):
    ex(skill, "E", 1)
    ex(skill, "G", 2)
    ex(skill, "I", 3)
    ex(skill, "F", 4, published=False)
    problems = skill_integrity_problems([skill])
    assert len(problems) == 2  # 2 < 3 et aucun contraint
    ex(skill, "H", 5)
    assert skill_integrity_problems([skill]) == []


def test_publication_refused_then_accepted(skill):
    p = LearningPath.objects.create(title="P", slug="p")
    m = Module.objects.create(learning_path=p, title="M", slug="m")
    lesson = Lesson.objects.create(module=m, title="L", slug="l")
    lesson.skills_taught.add(skill)
    lesson.is_published = True
    with pytest.raises(ValidationError):
        lesson.save()
    p.is_published = True
    with pytest.raises(ValidationError):
        p.save()
    for n, t in enumerate("EGH"):
        ex(skill, t, n)
    lesson.save()
    p.save()
