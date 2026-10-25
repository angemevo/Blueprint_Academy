"""Calcul de la maitrise des skills (issue #11).

Regles (validees par Ange) :

- seuls les exercices de PRODUCTION font bouger la maitrise ; les rappels
  (A/B/C/D) ne la changent jamais ;
- qualite d'une reussite : base + bonus de tentative + bonus de vitesse - indices ;
  on retient la MEILLEURE reussite par exercice ; un exercice jamais reussi vaut 0 ;
- maitrise = moyenne ponderee des qualites des exercices NON-I, ramenee sur 100
  (la qualite maximale possible correspond a 100 %) ;
- le type I n'ajoute qu'un bonus plafonne, jamais necessaire pour atteindre 100 ;
- un echec ne fait jamais baisser la maitrise acquise.

Tous les chiffres viennent de `settings.MASTERY_SETTINGS`.
"""

from django.conf import settings
from django.db import transaction
from django.db.models import Avg
from django.utils import timezone

from apps.exercises.enums import ExerciseType
from apps.exercises.models import Exercise, ExerciseAttempt
from apps.learning.models import Skill
from apps.progress.models import SkillMastery


def _cfg() -> dict:
    return settings.MASTERY_SETTINGS


def mastery_threshold() -> int:
    return _cfg()["mastered_threshold"]


def max_quality() -> int:
    """Qualite maximale d'une reussite (premiere tentative, rapide, sans indice)."""
    cfg = _cfg()
    bonuses = cfg["attempt_bonuses"]
    return cfg["success_base"] + (max(bonuses) if bonuses else 0) + cfg["speed_bonus"]


def _average_duration(exercise: Exercise, user) -> float | None:
    avg = (
        ExerciseAttempt.objects.filter(
            exercise=exercise, is_correct=True, duration_seconds__isnull=False
        )
        .exclude(user=user)
        .aggregate(a=Avg("duration_seconds"))["a"]
    )
    return avg


def attempt_quality(attempt: ExerciseAttempt, average_duration: float | None) -> int:
    """Points de qualite (>= 0) d'une tentative ; 0 si elle est ratee."""
    if not attempt.is_correct:
        return 0
    cfg = _cfg()
    bonuses = cfg["attempt_bonuses"]
    index = attempt.attempt_number - 1
    points = cfg["success_base"] + (bonuses[index] if index < len(bonuses) else 0)
    if average_duration is None or attempt.duration_seconds is None:
        points += cfg["speed_bonus_default"]
    elif attempt.duration_seconds < average_duration:
        points += cfg["speed_bonus"]
    penalty = min(attempt.hints_used * cfg["hint_penalty"], cfg["hint_penalty_max"])
    return max(points - penalty, 0)


def _best_ratio(user, exercise: Exercise) -> float:
    """Meilleure qualite de l'utilisateur sur l'exercice, entre 0 et 1."""
    average = _average_duration(exercise, user)
    attempts = ExerciseAttempt.objects.filter(
        user=user, exercise=exercise, is_correct=True
    )
    best = max((attempt_quality(a, average) for a in attempts), default=0)
    return min(best / max_quality(), 1.0)


def _weight(exercise: Exercise) -> float:
    return float(_cfg()["difficulty_weights"].get(exercise.difficulty, 1))


def production_exercises(skill: Skill):
    return Exercise.objects.filter(
        skills=skill, is_practice=True, is_published=True
    ).distinct()


def compute_mastery_score(user, skill: Skill) -> int:
    """Score 0-100 recalcule depuis les tentatives (sans plancher)."""
    core = [
        e
        for e in production_exercises(skill)
        if e.type != ExerciseType.UNREAL_EXPORT
    ]
    total_weight = sum(_weight(e) for e in core)
    score = (
        100 * sum(_weight(e) * _best_ratio(user, e) for e in core) / total_weight
        if total_weight
        else 0.0
    )
    unreal = [
        e
        for e in production_exercises(skill)
        if e.type == ExerciseType.UNREAL_EXPORT
    ]
    if unreal:
        ratio = sum(_best_ratio(user, e) for e in unreal) / len(unreal)
        score += _cfg()["unreal_bonus_max"] * ratio
    return min(round(score), 100)


def update_skill_mastery(user, exercise: Exercise, is_correct: bool) -> list[SkillMastery]:
    """Met a jour la maitrise des skills de l'exercice apres une tentative.

    Sans effet pour un exercice de rappel. A appeler dans la transaction de
    soumission, apres creation de la tentative.
    """
    if not exercise.is_practice:
        return []
    updated = []
    with transaction.atomic():
        for skill in exercise.skills.all():
            mastery, _ = SkillMastery.objects.select_for_update().get_or_create(
                user=user, skill=skill
            )
            mastery.attempts_count += 1
            if is_correct:
                mastery.successes_count += 1
            # Un echec ne fait jamais redescendre la maitrise acquise.
            mastery.mastery_score = max(
                mastery.mastery_score, compute_mastery_score(user, skill)
            )
            mastery.last_practiced_at = timezone.now()
            mastery.save()
            updated.append(mastery)
    return updated
