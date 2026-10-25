"""Controle d'integrite du contenu : chaque Skill doit pouvoir etre maitrisee.

CLAUDE.md : la maitrise doit pouvoir atteindre 100 % sans aucun exercice de
type I. Chaque Skill enseignee doit donc disposer d'assez d'exercices de
production NON-I publies, dont au moins un exercice contraint. Seuils dans
`settings.MASTERY_SETTINGS`. Le controle est appele a la publication d'une
lecon ou d'un parcours ; il l'est aussi par le test du seed.
Publier d'abord les exercices, puis la lecon.
"""

from django.conf import settings
from django.core.exceptions import ValidationError

from apps.exercises.enums import ExerciseType
from apps.exercises.models import Exercise
from apps.learning.models import LearningPath, Lesson, Skill


def skill_integrity_problems(skills) -> list[str]:
    """Messages (vides si tout va bien) pour les skills qui ne sont pas maitrisables."""
    cfg = settings.MASTERY_SETTINGS
    problems = []
    for skill in skills:
        exercises = Exercise.objects.filter(
            skills=skill, is_practice=True, is_published=True
        ).exclude(type=ExerciseType.UNREAL_EXPORT)
        total = exercises.count()
        constrained = exercises.filter(type__in=cfg["constrained_types"]).count()
        if total < cfg["min_production_exercises"]:
            problems.append(
                f"Skill « {skill.name} » : {total} exercice(s) de production "
                f"hors type I publie(s), {cfg['min_production_exercises']} requis."
            )
        if constrained < cfg["min_constrained_exercises"]:
            problems.append(
                f"Skill « {skill.name} » : {constrained} exercice(s) contraint(s) "
                f"({'/'.join(cfg['constrained_types'])}), "
                f"{cfg['min_constrained_exercises']} requis."
            )
    return problems


def lesson_skills(lesson: Lesson):
    return lesson.skills_taught.all()


def path_skills(path: LearningPath):
    return Skill.objects.filter(
        taught_by_lessons__module__learning_path=path
    ).distinct()


def ensure_publishable(instance) -> None:
    """Leve `ValidationError` si la lecon ou le parcours ne peut etre publie."""
    if instance.pk is None:
        return  # Les skills (M2M) n'existent pas avant la 1re sauvegarde.
    skills = path_skills(instance) if isinstance(instance, LearningPath) else lesson_skills(instance)
    problems = skill_integrity_problems(skills)
    if problems:
        raise ValidationError({"is_published": problems})
