"""Admin de contenu : creation sans code, erreurs sous le bon champ."""

import json

import pytest
from django.urls import reverse

from apps.exercises.models import Exercise
from apps.learning.models import LearningPath, Lesson, Module

PRINT = "K2Node_CallFunction:PrintString"
B_CONTENT = {"question": "Q", "options": [{"id": "o1", "text": "x"}, {"id": "o2", "text": "y"}]}
B_SOLUTION = {"correct_option_ids": ["o1"], "explanation": "ok"}
E_CONTENT = {"prompt": "p", "palette": [{"type": PRINT}]}
E_SOLUTION = {"required_nodes": [{"type": PRINT, "min_count": 1}]}


@pytest.fixture
def admin(client, django_user_model):
    user = django_user_model.objects.create_superuser(
        username="root", email="root@example.com", password="pw-12345-xyz"
    )
    client.force_login(user)
    return client


def add(client, model, data):
    return client.post(reverse(f"admin:{model}_add"), data)


def exercise_data(lesson, t, content, solution, slug):
    return {
        "lesson": lesson.pk, "type": t, "title": slug, "slug": slug,
        "content": json.dumps(content), "solution": json.dumps(solution),
        "hints": "[]", "difficulty": "beginner", "order": 0,
    }


@pytest.fixture
def lesson(db):
    p = LearningPath.objects.create(title="P", slug="p")
    m = Module.objects.create(learning_path=p, title="M", slug="m")
    return Lesson.objects.create(module=m, title="L", slug="l")


def test_changelists_load(admin, lesson):
    for name in ("skill", "learningpath", "module", "lesson"):
        assert admin.get(reverse(f"admin:learning_{name}_changelist")).status_code == 200
    assert admin.get(reverse("admin:exercises_exercise_changelist") + "?type=B").status_code == 200
    assert admin.get(reverse("admin:learning_learningpath_change", args=[lesson.module.learning_path.pk])).status_code == 200


def test_superuser_builds_path_module_lesson_exercise(admin):
    r = add(admin, "learning_learningpath", {"title": "Parcours", "slug": "parcours", "difficulty": "beginner", "estimated_hours": 1, "order": 0,
        "modules-TOTAL_FORMS": 0, "modules-INITIAL_FORMS": 0})
    assert r.status_code == 302
    path = LearningPath.objects.get(slug="parcours")
    r = add(admin, "learning_module", {"learning_path": path.pk, "title": "Mod", "slug": "mod", "order": 0,
        "lessons-TOTAL_FORMS": 0, "lessons-INITIAL_FORMS": 0})
    assert r.status_code == 302
    module = Module.objects.get(slug="mod")
    r = add(admin, "learning_lesson", {
        "module": module.pk, "title": "Lec", "slug": "lec", "order": 0,
        "content": json.dumps({"version": 1, "blocks": []}),
        "estimated_minutes": 5, "xp_reward": 10,
    })
    assert r.status_code == 302, getattr(r, "context", None) and r.context["adminform"].form.errors
    lesson = Lesson.objects.get(slug="lec")
    r = add(admin, "exercises_exercise", exercise_data(lesson, "B", B_CONTENT, B_SOLUTION, "qcm"))
    assert r.status_code == 302
    assert Exercise.objects.get(slug="qcm").is_practice is False


def test_invalid_solution_is_refused_on_the_solution_field(admin, lesson):
    bad = {"correct_option_ids": ["inconnu"]}
    r = add(admin, "exercises_exercise", exercise_data(lesson, "B", B_CONTENT, bad, "bad"))
    assert r.status_code == 200
    assert r.context["adminform"].form.errors.get("solution")
    assert not Exercise.objects.filter(slug="bad").exists()


def test_production_exercise_is_validated_too(admin, lesson):
    r = add(admin, "exercises_exercise", exercise_data(lesson, "E", E_CONTENT, {}, "e-bad"))
    assert r.status_code == 200
    assert r.context["adminform"].form.errors.get("solution")
    r = add(admin, "exercises_exercise", exercise_data(lesson, "E", E_CONTENT, E_SOLUTION, "e-ok"))
    assert r.status_code == 302
    assert Exercise.objects.get(slug="e-ok").is_practice is True


def test_invalid_json_text_is_a_field_error(admin, lesson):
    data = exercise_data(lesson, "B", B_CONTENT, B_SOLUTION, "j")
    data["content"] = "{pas du json"
    r = add(admin, "exercises_exercise", data)
    assert r.status_code == 200
    assert r.context["adminform"].form.errors.get("content")


def test_publishing_refused_by_integrity_is_not_a_500(admin, django_user_model):
    p = LearningPath.objects.create(title="P2", slug="p2")
    m = Module.objects.create(learning_path=p, title="M", slug="m2")
    from apps.learning.models import Skill
    s = Skill.objects.create(name="S", slug="s")
    lesson = Lesson.objects.create(module=m, title="L2", slug="l2")
    lesson.skills_taught.add(s)
    r = admin.post(reverse("admin:learning_lesson_change", args=[lesson.pk]), {
        "module": m.pk, "title": "L2", "slug": "l2", "order": 0, "is_published": "on",
        "content": json.dumps({"version": 1, "blocks": []}),
        "estimated_minutes": 5, "xp_reward": 10, "skills_taught": [s.pk],
    })
    assert r.status_code in (200, 302)
    lesson.refresh_from_db()
    assert lesson.is_published is False


# --- Publication avec controle d'integrite -------------------------------


def _taught_lesson(slug, with_exercises):
    from apps.learning.models import Skill

    p = LearningPath.objects.create(title=f"P-{slug}", slug=f"p-{slug}")
    m = Module.objects.create(learning_path=p, title="M", slug=f"m-{slug}")
    s = Skill.objects.create(name=f"Skill {slug}", slug=f"s-{slug}")
    lesson = Lesson.objects.create(module=m, title="L", slug=f"l-{slug}")
    lesson.skills_taught.add(s)
    if with_exercises:
        from django.conf import settings

        n = settings.MASTERY_SETTINGS["min_production_exercises"]
        ctypes = settings.MASTERY_SETTINGS["constrained_types"]
        for i in range(n):
            e = Exercise(
                lesson=lesson, type="E", title=f"e{i}", slug=f"e{i}-{slug}",
                content=E_CONTENT, solution=E_SOLUTION, is_published=True,
            )
            e.save()
            e.skills.add(s)
        # Exercice contraint : on force le type via update (contenu non pertinent ici).
        Exercise.objects.filter(pk=Exercise.objects.filter(lesson=lesson).first().pk).update(type=ctypes[0])
    return p, m, lesson


def _run(admin, name, obj):
    return admin.post(
        reverse(f"admin:learning_{name}_changelist"),
        {"action": "publier", "_selected_action": [obj.pk]},
        follow=True,
    )


def test_publish_lesson_refused_with_explicit_message(admin):
    _, _, lesson = _taught_lesson("ko", False)
    r = _run(admin, "lesson", lesson)
    assert r.status_code == 200
    lesson.refresh_from_db()
    assert lesson.is_published is False
    assert "Skill ko" in r.content.decode()


def test_publish_complete_lesson_succeeds(admin):
    _, _, lesson = _taught_lesson("ok", True)
    _run(admin, "lesson", lesson)
    lesson.refresh_from_db()
    assert lesson.is_published is True


def test_publish_path_checked_through_its_lessons(admin):
    p, _, _ = _taught_lesson("pko", False)
    r = _run(admin, "learningpath", p)
    p.refresh_from_db()
    assert p.is_published is False
    assert "Skill pko" in r.content.decode()
    p2, _, _ = _taught_lesson("pok", True)
    _run(admin, "learningpath", p2)
    p2.refresh_from_db()
    assert p2.is_published is True


def test_publish_module_checked_and_unpublish(admin):
    _, m, _ = _taught_lesson("mko", False)
    _run(admin, "module", m)
    m.refresh_from_db()
    assert m.is_published is False
    _, m2, _ = _taught_lesson("mok", True)
    _run(admin, "module", m2)
    m2.refresh_from_db()
    assert m2.is_published is True
    admin.post(
        reverse("admin:learning_module_changelist"),
        {"action": "depublier", "_selected_action": [m2.pk]},
    )
    m2.refresh_from_db()
    assert m2.is_published is False


def test_form_checkbox_follows_same_rule(admin):
    p, m, lesson = _taught_lesson("frm", False)
    r = admin.post(reverse("admin:learning_lesson_change", args=[lesson.pk]), {
        "module": m.pk, "title": "L", "slug": lesson.slug, "order": 0, "is_published": "on",
        "content": json.dumps({"version": 1, "blocks": []}),
        "estimated_minutes": 5, "xp_reward": 10,
        "skills_taught": [lesson.skills_taught.first().pk],
    })
    assert r.status_code == 200
    assert "Skill frm" in r.content.decode()
    lesson.refresh_from_db()
    assert lesson.is_published is False
