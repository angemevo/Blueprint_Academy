"""Attribution d'XP via le ledger `XPTransaction` et calcul du niveau.

Le ledger est la source de verite ; `Profile.total_xp` et `Profile.level` ne
sont que des caches, mis a jour ici et nulle part ailleurs.
"""

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Sum

from apps.exercises.enums import ExerciseType
from apps.gamification.models import XPSource, XPTransaction
from apps.users.models import Profile


def level_for_xp(total_xp: int) -> int:
    """Niveau atteint (>= 1) pour une XP cumulee, selon `XP_LEVEL_THRESHOLDS`."""
    reached = sum(1 for t in settings.XP_LEVEL_THRESHOLDS if total_xp >= t)
    return max(reached, 1)


def _refresh_cache(user) -> Profile:
    total = (
        XPTransaction.objects.filter(user=user).aggregate(s=Sum("amount"))["s"] or 0
    )
    total = max(total, 0)
    profile, _ = Profile.objects.select_for_update().get_or_create(user=user)
    profile.total_xp = total
    profile.level = level_for_xp(total)
    profile.save(update_fields=["total_xp", "level", "updated_at"])
    return profile


def recompute_user_cache(user) -> Profile:
    """Recalcule `total_xp` et `level` d'un utilisateur depuis le ledger."""
    with transaction.atomic():
        return _refresh_cache(user)


def award_exercise_xp(user, exercise) -> XPTransaction | None:
    """Credite l'XP de la premiere reussite ; renvoie None si deja attribuee."""
    source = (
        XPSource.CHALLENGE_SOLVED
        if exercise.type == ExerciseType.CHALLENGE
        else XPSource.EXERCISE_SOLVED
    )
    try:
        with transaction.atomic():
            tx, created = XPTransaction.objects.get_or_create(
                user=user,
                source=source,
                reference_key=f"exercise:{exercise.pk}",
                defaults={
                    "amount": exercise.effective_xp_reward,
                    "metadata": {"exercise_type": exercise.type},
                },
            )
            if not created:
                return None
            _refresh_cache(user)
            return tx
    except IntegrityError:
        return None
