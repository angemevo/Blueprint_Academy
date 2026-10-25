"""Progression des lecons, verrouillage par prerequis de Skills, parcours.

Une lecon est accessible si tous les Skills prerequis sont maitrises
(`SkillMastery.is_mastered`, seuil porte par le modele). Les prerequis sont
`Lesson.required_skills` plus les `Skill.prerequisites` des skills enseignes.
La maitrise ne vient que des exercices de production (A/B/D ne debloquent rien).
"""

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.learning.models import LearningPath, Lesson, Skill
from apps.progress.models import CourseProgress, LessonProgress, SkillMastery
from common.enums import CompletionStatus


class LessonLocked(Exception):
    """Lecon verrouillee ; `missing` liste les Skills a maitriser."""

    def __init__(self, missing):
        self.missing = list(missing)
        super().__init__("Lecon verrouillee.")


def required_skill_ids(lesson: Lesson) -> set[int]:
    taught = {s.id for s in lesson.skills_taught.all()}
    required = {s.id for s in lesson.required_skills.all()}
    required |= set(
        Skill.objects.filter(unlocks__in=taught).values_list("id", flat=True)
    )
    return required - taught


def mastered_skill_ids(user) -> set[int]:
    return {
        m.skill_id
        for m in SkillMastery.objects.filter(
            user=user, mastery_score__gte=settings.MASTERY_SETTINGS["mastered_threshold"]
        )
    }


def missing_skills(user, lesson: Lesson, mastered: set[int] | None = None):
    needed = required_skill_ids(lesson)
    if not needed:
        return []
    mastered = mastered_skill_ids(user) if mastered is None else mastered
    return list(Skill.objects.filter(id__in=needed - mastered).order_by("name"))


def is_unlocked(user, lesson: Lesson) -> bool:
    return not missing_skills(user, lesson)


def _ensure_unlocked(user, lesson):
    missing = missing_skills(user, lesson)
    if missing:
        raise LessonLocked(missing)


@transaction.atomic
def start_lesson(user, lesson: Lesson) -> LessonProgress:
    _ensure_unlocked(user, lesson)
    now = timezone.now()
    lp, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    lp.last_viewed_at = now
    if lp.status == CompletionStatus.NOT_STARTED:
        lp.status = CompletionStatus.IN_PROGRESS
        lp.started_at = now
    lp.save()
    recompute_course(user, lesson.module.learning_path)
    return lp


@transaction.atomic
def complete_lesson(user, lesson: Lesson) -> LessonProgress:
    _ensure_unlocked(user, lesson)
    now = timezone.now()
    lp, _ = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
    lp.started_at = lp.started_at or now
    lp.last_viewed_at = now
    if lp.status != CompletionStatus.COMPLETED:
        lp.status = CompletionStatus.COMPLETED
        lp.completed_at = now
    lp.save()
    recompute_course(user, lesson.module.learning_path)
    return lp


def recompute_course(user, path: LearningPath) -> CourseProgress:
    """Recalcule le cache : part des lecons publiees du parcours terminees."""
    lesson_ids = list(
        Lesson.objects.filter(
            module__learning_path=path, module__is_published=True, is_published=True
        ).values_list("id", flat=True)
    )
    done = LessonProgress.objects.filter(
        user=user, lesson_id__in=lesson_ids, status=CompletionStatus.COMPLETED
    ).count()
    started = LessonProgress.objects.filter(
        user=user, lesson_id__in=lesson_ids
    ).exists()
    percent = round(100 * done / len(lesson_ids)) if lesson_ids else 0
    cp, _ = CourseProgress.objects.get_or_create(user=user, learning_path=path)
    now = timezone.now()
    cp.completion_percent = percent
    if lesson_ids and done == len(lesson_ids):
        cp.status = CompletionStatus.COMPLETED
        cp.completed_at = cp.completed_at or now
    elif started:
        cp.status = CompletionStatus.IN_PROGRESS
        cp.completed_at = None
    if started and not cp.started_at:
        cp.started_at = now
    cp.save()
    return cp


def progress_overview(user, paths) -> list[dict]:
    """Progression par parcours avec l'etat ouvert/verrouille de chaque lecon."""
    mastered = mastered_skill_ids(user)
    statuses = dict(
        LessonProgress.objects.filter(user=user).values_list("lesson_id", "status")
    )
    out = []
    for path in paths:
        cp = CourseProgress.objects.filter(user=user, learning_path=path).first()
        lessons = []
        qs = (
            Lesson.objects.filter(
                module__learning_path=path,
                module__is_published=True,
                is_published=True,
            )
            .select_related("module")
            .prefetch_related("skills_taught", "required_skills")
            .order_by("module__order", "order", "title")
        )
        for lesson in qs:
            missing = missing_skills(user, lesson, mastered)
            lessons.append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "status": statuses.get(lesson.id, CompletionStatus.NOT_STARTED),
                    "locked": bool(missing),
                    "missing_skills": [{"id": s.id, "name": s.name} for s in missing],
                }
            )
        out.append(
            {
                "learning_path": {"id": path.id, "slug": path.slug, "title": path.title},
                "status": cp.status if cp else CompletionStatus.NOT_STARTED,
                "completion_percent": cp.completion_percent if cp else 0,
                "lessons": lessons,
            }
        )
    return out
