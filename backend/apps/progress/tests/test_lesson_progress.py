import pytest
from rest_framework.test import APIClient

from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.progress.models import CourseProgress, SkillMastery
from apps.users.models import Profile, User


def make_client(name):
    u = User.objects.create_user(username=name, password="Zx9!longpassword42")
    Profile.objects.create(user=u)
    c = APIClient()
    c.force_authenticate(u)
    return c, u


@pytest.fixture
def world(db):
    base = Skill.objects.create(name="Variables", slug="variables")
    adv = Skill.objects.create(name="Events", slug="events")
    adv.prerequisites.add(base)
    p = LearningPath.objects.create(title="P", slug="p", is_published=True)
    m = Module.objects.create(learning_path=p, title="M", slug="m", is_published=True)
    l1 = Lesson.objects.create(module=m, title="L1", slug="l1", order=1, is_published=True)
    l2 = Lesson.objects.create(module=m, title="L2", slug="l2", order=2, is_published=True)
    l1.skills_taught.add(base)
    l2.skills_taught.add(adv)  # prerequis implicite : base
    return p, l1, l2, base


def test_complete_all_lessons_gives_100(world):
    p, l1, l2, base = world
    c, u = make_client("a")
    assert c.post(f"/api/lessons/{l1.id}/start/").status_code == 200
    assert c.post(f"/api/lessons/{l1.id}/complete/").status_code == 200
    assert CourseProgress.objects.get(user=u).completion_percent == 50
    SkillMastery.objects.create(user=u, skill=base, mastery_score=100)
    assert c.post(f"/api/lessons/{l2.id}/complete/").data["status"] == "completed"
    cp = CourseProgress.objects.get(user=u)
    assert cp.completion_percent == 100 and cp.status == "completed"


def test_locked_lesson_refused_with_missing_skills(world):
    p, l1, l2, base = world
    c, u = make_client("b")
    for action in ("start", "complete"):
        r = c.post(f"/api/lessons/{l2.id}/{action}/")
        assert r.status_code == 403
        assert [s["name"] for s in r.data["missing_skills"]] == ["Variables"]
    SkillMastery.objects.create(user=u, skill=base, mastery_score=10)
    assert c.post(f"/api/lessons/{l2.id}/start/").status_code == 403


def test_required_skills_of_lesson_also_lock(world):
    p, l1, l2, base = world
    l1.required_skills.add(Skill.objects.create(name="Autre", slug="autre"))
    c, _ = make_client("c")
    assert c.post(f"/api/lessons/{l1.id}/start/").status_code == 403


def test_progress_overview_reports_locked_state(world):
    p, l1, l2, base = world
    c, _ = make_client("d")
    r = c.get("/api/progress/")
    lessons = r.data["results"][0]["lessons"]
    assert [x["locked"] for x in lessons] == [False, True]
    assert lessons[1]["missing_skills"][0]["name"] == "Variables"


def test_users_only_see_own_progress(world):
    p, l1, l2, base = world
    c1, _ = make_client("e")
    c2, _ = make_client("f")
    c1.post(f"/api/lessons/{l1.id}/complete/")
    r = c2.get("/api/progress/")
    assert r.data["results"][0]["completion_percent"] == 0
    assert r.data["results"][0]["lessons"][0]["status"] == "not_started"
    assert CourseProgress.objects.count() == 1


def test_auth_required(world):
    p, l1, *_ = world
    assert APIClient().post(f"/api/lessons/{l1.id}/start/").status_code in (401, 403)
    assert APIClient().get("/api/progress/").status_code in (401, 403)
