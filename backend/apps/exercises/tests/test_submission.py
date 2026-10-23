import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from django.db import IntegrityError, connection, transaction

from apps.exercises.models import ExerciseAttempt
from apps.exercises.services import submission as service
from apps.exercises.tests.test_exercise_api import SECRET, client_for, make
from apps.exercises.tests.test_exercise_api import lesson as _lesson_fixture
from apps.users.models import Role

pytestmark = pytest.mark.django_db

lesson = _lesson_fixture


def url(ex):
    return f"/api/exercises/{ex.pk}/submit/"


def test_requires_auth(lesson):
    ex = make(lesson, "A")
    assert client_for().post(url(ex), {"submission": {"answer": "x"}}, format="json").status_code in (401, 403)


def test_submit_records_attempt_without_leak(lesson):
    ex = make(lesson, "A")
    c = client_for(Role.STUDENT)
    r = c.post(url(ex), {"submission": {"answer": SECRET}, "duration_seconds": 12, "hints_used": 1}, format="json")
    assert r.status_code == 200
    body = r.json()
    assert body["is_correct"] is True and body["attempt_number"] == 1
    a = ExerciseAttempt.objects.get()
    assert (a.duration_seconds, a.hints_used, a.attempt_number, a.submission) == (12, 1, 1, {"answer": SECRET})
    r2 = c.post(url(ex), {"submission": {"answer": "faux"}}, format="json")
    assert r2.json()["attempt_number"] == 2
    assert "solution" not in json.dumps(r2.json()) and "INDICE-SECRET" not in json.dumps(r2.json())


def test_missing_submission_is_400(lesson):
    ex = make(lesson, "A")
    assert client_for(Role.STUDENT).post(url(ex), {}, format="json").status_code == 400


def test_max_attempts_gives_409(lesson):
    ex = make(lesson, "A")  # max_attempts=3
    c = client_for(Role.STUDENT)
    for _ in range(3):
        assert c.post(url(ex), {"submission": {"answer": "x"}}, format="json").status_code == 200
    assert c.post(url(ex), {"submission": {"answer": "x"}}, format="json").status_code == 409
    assert ExerciseAttempt.objects.count() == 3


@pytest.mark.parametrize("t", ["E", "F", "G", "H", "I"])
def test_production_types_give_501(lesson, t):
    from apps.exercises.validators import default_registry

    if t in {k.value for k in default_registry._validators}:
        pytest.skip("validateur livre")
    ex = make(lesson, t)
    r = client_for(Role.STUDENT).post(url(ex), {"submission": {}}, format="json")
    assert r.status_code == 501 and r.json()["detail"]
    assert ExerciseAttempt.objects.count() == 0


def test_unpublished_exercise_404_for_student(lesson):
    ex = make(lesson, "A", published=False)
    assert client_for(Role.STUDENT).post(url(ex), {"submission": {"answer": "x"}}, format="json").status_code == 404


def test_unique_number_constraint(lesson):
    ex = make(lesson, "A")
    c = client_for(Role.STUDENT)
    c.post(url(ex), {"submission": {"answer": "x"}}, format="json")
    a = ExerciseAttempt.objects.get()
    with pytest.raises(IntegrityError), transaction.atomic():
        ExerciseAttempt.objects.create(user=a.user, exercise=ex, attempt_number=1)


@pytest.mark.django_db(transaction=True)
def test_concurrent_submissions_get_distinct_numbers(lesson):
    ex = make(lesson, "A")
    ex.max_attempts = None
    ex.save()
    user = client_for(Role.STUDENT).handler._force_user

    def go(_):
        try:
            return service.submit_exercise(user, ex, {"answer": "x"})[0].attempt_number
        finally:
            connection.close()

    with ThreadPoolExecutor(4) as pool:
        numbers = list(pool.map(go, range(4)))
    assert sorted(numbers) == [1, 2, 3, 4]
