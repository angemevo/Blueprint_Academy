import pytest
from django.core.management import call_command

from apps.exercises.models import Exercise
from apps.learning.models import LearningPath, Lesson, Module, Skill
from apps.learning.services.integrity import skill_integrity_problems
from apps.learning.services.publication import publish


@pytest.mark.django_db
def test_seed_deux_fois_sans_doublon():
    call_command("seed_blueprint")
    counts = (Skill.objects.count(), LearningPath.objects.count(), Module.objects.count())
    call_command("seed_blueprint")
    assert (Skill.objects.count(), LearningPath.objects.count(), Module.objects.count()) == counts
    assert counts[1] == 1 and counts[0] > 0 and counts[2] > 0


@pytest.mark.django_db
def test_parcours_et_modules_non_publies():
    call_command("seed_blueprint")
    path = LearningPath.objects.get(slug="blueprint-fundamentals")
    assert not path.is_published
    assert path.modules.count() > 0
    assert not path.modules.filter(is_published=True).exists()


@pytest.mark.django_db
def test_premier_module_non_publie_sans_doublon():
    call_command("seed_blueprint")
    counts = (Lesson.objects.count(), Exercise.objects.count())
    call_command("seed_blueprint")
    assert (Lesson.objects.count(), Exercise.objects.count()) == counts
    assert counts[0] >= 2 and counts[1] >= 6
    assert not Lesson.objects.filter(is_published=True).exists()
    assert not Exercise.objects.filter(is_published=True).exists()


@pytest.mark.django_db
def test_exercices_du_seed_valides_et_non_resolus_au_depart():
    from apps.exercises.schemas import validate_exercise_payload

    call_command("seed_blueprint")
    for ex in Exercise.objects.all():
        validate_exercise_payload(ex.type, ex.content, ex.solution)


@pytest.mark.django_db
def test_integrite_ok_une_fois_le_module_publie():
    call_command("seed_blueprint")
    module = Module.objects.get(slug="prise-en-main-editeur")
    skills = Skill.objects.filter(taught_by_lessons__module=module).distinct()
    assert skills.count() == 2
    assert skill_integrity_problems(skills)  # rien de publie : refuse
    Exercise.objects.update(is_published=True)
    assert skill_integrity_problems(skills) == []
    assert publish(module) == []
    for lesson in module.lessons.all():
        assert publish(lesson) == []
