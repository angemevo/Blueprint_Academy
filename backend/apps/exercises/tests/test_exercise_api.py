import json
import random

import pytest
from rest_framework.test import APIClient

from apps.exercises.models import Exercise
from apps.exercises.services.catalog import shuffle_ordering_items
from apps.learning.models import LearningPath, Lesson, Module
from apps.users.models import Profile, Role, User

PW = "Zx9!longpassword42"
SECRET = "SECRET-SOLUTION-MARKER"


def client_for(role=None):
    c = APIClient()
    if role:
        u = User.objects.create_user(username=role, password=PW, role=role)
        Profile.objects.create(user=u)
        c.force_authenticate(u)
    return c


BEGIN = "K2Node_Event:ReceiveBeginPlay"
PRINT = "K2Node_CallFunction:PrintString"
GRAPH = {"nodes": [{"id": "n1", "type": BEGIN}], "edges": []}
PALETTE = [{"type": BEGIN}, {"type": PRINT}]
PROD_SOL = {"required_nodes": [{"type": PRINT, "min_count": 1, "feedback": SECRET}]}

SPECS = {
    "A": ({"question": "Q ?"}, {"accepted_answers": [SECRET], "explanation": SECRET}),
    "B": (
        {"question": "Q", "options": [{"id": "o1", "text": "x"}, {"id": "o2", "text": "y"}]},
        {"correct_option_ids": ["o1"], "explanation": SECRET},
    ),
    "C": (
        {"items": [{"id": f"i{k}", "label": f"L{k}"} for k in range(5)]},
        {"order": [f"i{k}" for k in range(5)], "explanation": SECRET},
    ),
    "D": (
        {
            "left": [{"id": "l1", "label": "a"}, {"id": "l2", "label": "b"}],
            "right": [{"id": "r1", "label": "c"}, {"id": "r2", "label": "d"}],
        },
        {"pairs": [{"left_id": "l1", "right_id": "r1"}, {"left_id": "l2", "right_id": "r2"}], "explanation": SECRET},
    ),
    "E": ({"prompt": "p", "palette": PALETTE}, PROD_SOL),
    "F": (
        {"prompt": "p", "broken_graph": GRAPH, "palette": PALETTE},
        {**PROD_SOL, "forbidden_nodes": [{"type": BEGIN}]},
    ),
    "G": ({"prompt": "p", "palette": PALETTE}, PROD_SOL),
    "H": ({"prompt": "p", "partial_graph": GRAPH, "palette": PALETTE}, PROD_SOL),
    "I": ({"prompt": "p", "instructions": ["step"]}, PROD_SOL),
}


@pytest.fixture
def lesson(db):
    p = LearningPath.objects.create(title="P", slug="p", is_published=True)
    m = Module.objects.create(learning_path=p, title="M", slug="m", is_published=True)
    return Lesson.objects.create(module=m, title="L", slug="l", is_published=True)


def make(lesson, t, published=True):
    content, solution = SPECS[t]
    return Exercise.objects.create(
        lesson=lesson, type=t, title=f"E{t}", slug=f"e-{t.lower()}",
        content=content, solution=solution, is_published=published,
        hints=["INDICE-SECRET"], time_limit_seconds=60, max_attempts=3,
    )


def test_requires_auth(lesson):
    ex = make(lesson, "A")
    assert client_for().get(f"/api/exercises/{ex.pk}/").status_code in (401, 403)


@pytest.mark.parametrize("t", list(SPECS))
def test_no_solution_leak_for_every_type(lesson, t):
    ex = make(lesson, t)
    r = client_for(Role.STUDENT).get(f"/api/exercises/{ex.pk}/")
    assert r.status_code == 200
    data = r.json()
    raw = json.dumps(data)
    assert SECRET not in raw and "INDICE-SECRET" not in raw
    for forbidden in ("solution", "hints\"", "required_nodes", "accepted_answers",
                      "correct_option_ids", "pairs", "feedback"):
        assert forbidden not in raw
    if t == "D":  # colonne de droite melangee : meme contenu, autre ordre
        assert data["content"]["left"] == ex.content["left"]
        by_id = lambda i: i["id"]  # noqa: E731
        assert sorted(data["content"]["right"], key=by_id) == sorted(ex.content["right"], key=by_id)
    elif t != "C":
        assert data["content"] == ex.content
    assert data["type"] == t and data["hints_count"] == 1
    assert data["time_limit_seconds"] == 60 and data["max_attempts"] == 3
    assert data["difficulty"]
    assert data["xp_reward"] == ex.effective_xp_reward


def test_unpublished_exercise_hidden_from_student_visible_to_staff(lesson):
    ex = make(lesson, "A", published=False)
    assert client_for(Role.STUDENT).get(f"/api/exercises/{ex.pk}/").status_code == 404
    assert client_for(Role.INSTRUCTOR).get(f"/api/exercises/{ex.pk}/").status_code == 200


def test_exercise_of_unpublished_lesson_hidden(lesson):
    ex = make(lesson, "A")
    Lesson.objects.filter(pk=lesson.pk).update(is_published=False)
    assert client_for(Role.STUDENT).get(f"/api/exercises/{ex.pk}/").status_code == 404


def test_ordering_is_shuffled_and_never_the_solution(lesson):
    ex = make(lesson, "C")
    c = client_for(Role.STUDENT)
    seen = set()
    for _ in range(30):
        ids = [i["id"] for i in c.get(f"/api/exercises/{ex.pk}/").json()["content"]["items"]]
        assert sorted(ids) == sorted(ex.solution["order"])
        assert ids != ex.solution["order"]
        seen.add(tuple(ids))
    assert len(seen) > 1


def test_matching_right_column_is_shuffled_and_hides_pairs(lesson):
    ex = make(lesson, "D")
    c = client_for(Role.STUDENT)
    expected = [p["right_id"] for p in ex.solution["pairs"]]  # partenaires dans l'ordre de gauche
    seen = set()
    for _ in range(30):
        body = c.get(f"/api/exercises/{ex.pk}/").json()
        assert [i["id"] for i in body["content"]["left"]] == ["l1", "l2"]
        ids = [i["id"] for i in body["content"]["right"]]
        assert sorted(ids) == sorted(expected)
        assert ids != expected
        assert SECRET not in json.dumps(body)
        seen.add(tuple(ids))
    assert seen


@pytest.mark.parametrize("seed", range(20))
def test_shuffle_two_items_never_returns_solution(seed):
    items = [{"id": "a"}, {"id": "b"}]
    out = shuffle_ordering_items(items, ["a", "b"], rng=random.Random(seed))
    assert [i["id"] for i in out] == ["b", "a"]


def test_shuffle_fallback_when_rng_is_identity():
    class NoShuffle:
        def shuffle(self, x):
            pass

    items = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    out = shuffle_ordering_items(items, ["a", "b", "c"], rng=NoShuffle())
    assert [i["id"] for i in out] != ["a", "b", "c"]


def test_lesson_detail_lists_exercises_without_content(lesson):
    make(lesson, "A")
    make(lesson, "B", published=False)
    r = client_for(Role.STUDENT).get(f"/api/lessons/{lesson.pk}/")
    assert r.status_code == 200
    assert r.json()["exercises"] == [{"id": r.json()["exercises"][0]["id"], "title": "EA", "type": "A"}]
    r = client_for(Role.INSTRUCTOR).get(f"/api/lessons/{lesson.pk}/")
    assert len(r.json()["exercises"]) == 2
