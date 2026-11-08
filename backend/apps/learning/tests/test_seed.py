import pytest
from django.core.management import call_command

from apps.learning.models import LearningPath, Module, Skill


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
