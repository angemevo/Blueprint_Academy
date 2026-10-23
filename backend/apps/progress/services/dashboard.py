"""Donnees du tableau de bord etudiant : lecture seule, requetes regroupees.

L'XP vient du ledger (`XPTransaction`), pas du cache `Profile.total_xp`.
Aucune `solution` d'exercice n'est lue ni renvoyee.
"""

from django.conf import settings
from django.db.models import Sum

from apps.exercises.models import ExerciseAttempt
from apps.gamification.models import XPTransaction
from apps.gamification.services.xp import level_for_xp
from apps.learning.models import Lesson
from apps.progress.models import CourseProgress, LessonProgress, SkillMastery
from common.enums import CompletionStatus

RECENT_ATTEMPTS = 5


def _xp_block(user) -> dict:
    total = max(
        XPTransaction.objects.filter(user=user).aggregate(s=Sum("amount"))["s"] or 0, 0
    )
    level = level_for_xp(total)
    thresholds = settings.XP_LEVEL_THRESHOLDS
    # Le niveau N demarre au seuil d'indice N-1 ; le suivant, a l'indice N.
    next_threshold = thresholds[level] if level < len(thresholds) else None
    return {
        "total_xp": total,
        "level": level,
        "next_level_xp": next_threshold,
        "xp_to_next_level": None if next_threshold is None else next_threshold - total,
    }


def _next_lesson(user, path, mastered: set[int]):
    lessons = (
        Lesson.objects.filter(
            module__learning_path=path, module__is_published=True, is_published=True
        )
        .prefetch_related("skills_taught__prerequisites", "required_skills")
        .order_by("module__order", "order", "title")
    )
    done = set(
        LessonProgress.objects.filter(
            user=user, status=CompletionStatus.COMPLETED
        ).values_list("lesson_id", flat=True)
    )
    for lesson in lessons:
        if lesson.id in done:
            continue
        taught = {s.id for s in lesson.skills_taught.all()}
        needed = {s.id for s in lesson.required_skills.all()}
        for s in lesson.skills_taught.all():
            needed |= {p.id for p in s.prerequisites.all()}
        if not (needed - taught) - mastered:
            return {"id": lesson.id, "title": lesson.title}
    return None


def build_dashboard(user) -> dict:
    masteries = list(SkillMastery.objects.filter(user=user).select_related("skill"))
    mastered = {m.skill_id for m in masteries if m.is_mastered}

    courses = list(
        CourseProgress.objects.filter(user=user, status=CompletionStatus.IN_PROGRESS)
        .select_related("learning_path")
        .order_by("-updated_at")
    )
    next_lesson = _next_lesson(user, courses[0].learning_path, mastered) if courses else None

    attempts = ExerciseAttempt.objects.filter(user=user).select_related("exercise")[
        :RECENT_ATTEMPTS
    ]
    return {
        **_xp_block(user),
        "current_paths": [
            {
                "id": c.learning_path_id,
                "slug": c.learning_path.slug,
                "title": c.learning_path.title,
                "completion_percent": c.completion_percent,
            }
            for c in courses
        ],
        "next_lesson": next_lesson,
        "recent_attempts": [
            {
                "id": a.id,
                "exercise": {
                    "id": a.exercise_id,
                    "title": a.exercise.title,
                    "type": a.exercise.type,
                },
                "is_correct": a.is_correct,
                "score": a.score,
                "attempt_number": a.attempt_number,
                "created_at": a.created_at,
            }
            for a in attempts
        ],
        "skills": [
            {
                "id": m.skill_id,
                "name": m.skill.name,
                "mastery_score": m.mastery_score,
                "is_mastered": m.is_mastered,
            }
            for m in masteries
        ],
    }
