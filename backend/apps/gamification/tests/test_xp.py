import pytest
from django.core.management import call_command

from apps.exercises.tests.test_exercise_api import SECRET, client_for, make
from apps.exercises.tests.test_exercise_api import lesson as _lesson
from apps.gamification.models import XPSource, XPTransaction
from apps.gamification.services.xp import level_for_xp
from apps.users.models import Profile, Role, User

pytestmark = pytest.mark.django_db
lesson = _lesson


def submit(c, ex, answer):
    return c.post(f"/api/exercises/{ex.pk}/submit/", {"submission": {"answer": answer}}, format="json")


def test_double_success_one_transaction(lesson):
    ex = make(lesson, "A")
    c = client_for(Role.STUDENT)
    submit(c, ex, SECRET)
    submit(c, ex, SECRET)
    tx = XPTransaction.objects.get()
    assert tx.amount == ex.effective_xp_reward
    assert tx.source == XPSource.EXERCISE_SOLVED and tx.reference_key == f"exercise:{ex.pk}"
    p = Profile.objects.get()
    assert p.total_xp == ex.effective_xp_reward


def test_failure_gives_nothing(lesson):
    ex = make(lesson, "A")
    submit(client_for(Role.STUDENT), ex, "faux")
    assert not XPTransaction.objects.exists()


def test_challenge_source(lesson):
    from apps.gamification.services.xp import award_exercise_xp

    ex = make(lesson, "G")
    u = User.objects.create_user(username="u", password="x")
    tx = award_exercise_xp(u, ex)
    assert tx.source == XPSource.CHALLENGE_SOLVED
    assert Profile.objects.get(user=u).total_xp == ex.effective_xp_reward


def test_level_from_settings(settings):
    settings.XP_LEVEL_THRESHOLDS = [0, 10, 30]
    assert [level_for_xp(x) for x in (0, 9, 10, 29, 30, 999)] == [1, 1, 2, 2, 3, 3]


def test_recompute_restores_cache():
    u = User.objects.create_user(username="u", password="x")
    XPTransaction.objects.create(user=u, amount=120, source=XPSource.MANUAL_ADJUSTMENT)
    Profile.objects.create(user=u, total_xp=9999, level=7)
    call_command("recompute_xp")
    p = Profile.objects.get(user=u)
    assert (p.total_xp, p.level) == (120, 2)
