import pytest
from rest_framework.test import APIClient

from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.users.models import Profile, Role, User


def client_for(role=None):
    c = APIClient()
    if role:
        u = User.objects.create_user(username=role, password="Zx9!longpassword42", role=role)
        Profile.objects.create(user=u)
        c.force_authenticate(u)
    return c


@pytest.fixture
def data(db):
    sk = Skill.objects.create(name="Variables", slug="variables")
    sk2 = Skill.objects.create(name="Events", slug="events")
    paths = []
    for i in range(3):
        p = LearningPath.objects.create(
            title=f"P{i}", slug=f"p{i}", order=3 - i, is_published=(i != 2)
        )
        paths.append(p)
        for j in range(2):
            m = Module.objects.create(
                learning_path=p, title=f"M{j}", slug=f"m{j}", order=j, is_published=(j == 0)
            )
            for k in range(3):
                les = Lesson.objects.create(
                    module=m, title=f"L{k}", slug=f"l{k}", order=k, is_published=(k != 2)
                )
                les.skills_taught.add(sk)
                les.required_skills.add(sk2)
    return paths


def test_list_public_published_only_sorted(data):
    r = client_for().get("/api/learning-paths/")
    assert r.status_code == 200
    assert [p["slug"] for p in r.data["results"]] == ["p1", "p0"]
    assert "count" in r.data


def test_detail_hides_unpublished_for_student_and_visitor(data):
    for c in (client_for(), client_for(Role.STUDENT)):
        r = c.get("/api/learning-paths/p0/")
        assert r.status_code == 200
        assert [m["slug"] for m in r.data["modules"]] == ["m0"]
        assert [x["slug"] for x in r.data["modules"][0]["lessons"]] == ["l0", "l1"]
        assert c.get("/api/learning-paths/p2/").status_code == 404


def test_staff_sees_unpublished(data):
    for role in (Role.INSTRUCTOR, Role.ADMIN):
        c = client_for(role)
        assert c.get("/api/learning-paths/p2/").status_code == 200
        r = c.get("/api/learning-paths/p0/")
        assert len(r.data["modules"]) == 2
        assert len(r.data["modules"][0]["lessons"]) == 3


def test_lesson_requires_auth(data):
    les = Lesson.objects.get(module__learning_path__slug="p0", module__slug="m0", slug="l0")
    assert client_for().get(f"/api/lessons/{les.id}/").status_code == 401


def test_lesson_detail_content_and_skills(data):
    les = Lesson.objects.get(module__learning_path__slug="p0", module__slug="m0", slug="l0")
    r = client_for(Role.STUDENT).get(f"/api/lessons/{les.id}/")
    assert r.status_code == 200
    assert "content" in r.data
    assert [s["slug"] for s in r.data["skills_taught"]] == ["variables"]
    assert [s["slug"] for s in r.data["required_skills"]] == ["events"]


def test_unpublished_lesson_hidden_from_student(data):
    draft = Lesson.objects.get(module__learning_path__slug="p0", module__slug="m0", slug="l2")
    in_draft_module = Lesson.objects.get(
        module__learning_path__slug="p0", module__slug="m1", slug="l0"
    )
    in_draft_path = Lesson.objects.filter(module__learning_path__slug="p2").first()
    student = client_for(Role.STUDENT)
    for lesson in (draft, in_draft_module, in_draft_path):
        assert student.get(f"/api/lessons/{lesson.id}/").status_code == 404
    assert client_for(Role.INSTRUCTOR).get(f"/api/lessons/{draft.id}/").status_code == 200


def test_list_query_count_bounded(data, django_assert_num_queries):
    c = client_for()
    with django_assert_num_queries(2):  # count + page
        c.get("/api/learning-paths/")


def test_detail_query_count_bounded(data, django_assert_num_queries):
    c = client_for()
    with django_assert_num_queries(3):  # parcours, modules, lecons
        c.get("/api/learning-paths/p0/")


def test_lesson_query_count_bounded(data, django_assert_num_queries):
    les = Lesson.objects.get(module__learning_path__slug="p0", module__slug="m0", slug="l0")
    c = client_for(Role.STUDENT)
    with django_assert_num_queries(4):  # lecon, skills enseignes, prerequis, exercices
        c.get(f"/api/lessons/{les.id}/")
