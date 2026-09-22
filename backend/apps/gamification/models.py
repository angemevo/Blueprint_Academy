"""Modeles de l'app gamification.

Perimetre : XPTransaction (ledger), Achievement, UserAchievement.

Points structurants (CLAUDE.md) :
- `XPTransaction` est la SOURCE DE VERITE de l'XP ; `users.Profile.total_xp`
  n'est qu'un cache recalculable ;
- les classements sont des REQUETES agregees sur ce ledger, pas une table.
"""

from django.core.exceptions import ValidationError
from django.db import models

from common.models import OrderedModel, TimeStampedModel

from .schemas import validate_achievement_rule


class XPSource(models.TextChoices):
    """Origine d'un gain (ou d'un ajustement) d'XP."""

    LESSON_COMPLETED = "lesson_completed", "Lecon terminee"
    EXERCISE_SOLVED = "exercise_solved", "Exercice reussi"
    CHALLENGE_SOLVED = "challenge_solved", "Challenge reussi"
    PROJECT_COMPLETED = "project_completed", "Projet termine"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked", "Succes debloque"
    STREAK_BONUS = "streak_bonus", "Bonus de serie"
    MANUAL_ADJUSTMENT = "manual_adjustment", "Ajustement manuel"


class XPTransaction(models.Model):
    """Ecriture immuable du ledger d'XP.

    Immuable par convention : on n'edite jamais une ligne, on en ajoute une
    nouvelle (eventuellement negative). D'ou l'absence de `updated_at`.

    `reference_key` rend l'attribution IDEMPOTENTE : refaire deux fois le meme
    exercice ne cree pas deux gains, la contrainte unique l'interdit.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="xp_transactions",
        verbose_name="utilisateur",
    )
    amount = models.IntegerField(
        "montant", help_text="Positif pour un gain, negatif pour une correction."
    )
    source = models.CharField(
        "origine", max_length=30, choices=XPSource.choices, db_index=True
    )
    reference_key = models.CharField(
        "cle de reference",
        max_length=120,
        blank=True,
        help_text="Identifie le fait generateur, par exemple 'exercise:42'.",
    )
    metadata = models.JSONField("metadonnees", default=dict, blank=True)
    created_at = models.DateTimeField("cree le", auto_now_add=True)

    class Meta:
        verbose_name = "transaction XP"
        verbose_name_plural = "transactions XP"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "source", "reference_key"],
                condition=~models.Q(reference_key=""),
                name="xptransaction_idempotent_reference",
            )
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"], name="xptx_user_date_idx"),
            # Sert les classements periodiques (agregation par fenetre de temps).
            models.Index(fields=["-created_at"], name="xptx_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} {self.amount:+d} XP ({self.get_source_display()})"


class Achievement(TimeStampedModel, OrderedModel):
    """Succes deverrouillable, defini par une regle declarative."""

    code = models.SlugField(
        "code", max_length=80, unique=True, help_text="Identifiant stable, non traduit."
    )
    name = models.CharField("nom", max_length=120)
    description = models.TextField("description", blank=True)
    icon = models.CharField(
        "icone", max_length=60, blank=True, help_text="Nom d'icone cote frontend."
    )
    xp_reward = models.PositiveIntegerField("XP a l'obtention", default=0)
    rule = models.JSONField(
        "regle",
        default=dict,
        help_text='Exemple : {"type": "exercises_solved", "threshold": 25}.',
    )
    is_secret = models.BooleanField(
        "secret", default=False, help_text="Masque tant qu'il n'est pas obtenu."
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "succes"
        verbose_name_plural = "succes"
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        try:
            validate_achievement_rule(self.rule)
        except ValidationError as exc:
            raise ValidationError({"rule": exc.messages}) from exc

    def save(self, *args, **kwargs):
        validate_achievement_rule(self.rule)
        return super().save(*args, **kwargs)


class UserAchievement(models.Model):
    """Succes obtenu par un utilisateur."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="utilisateur",
    )
    achievement = models.ForeignKey(
        "gamification.Achievement",
        on_delete=models.CASCADE,
        related_name="unlocked_by",
        verbose_name="succes",
    )
    unlocked_at = models.DateTimeField("obtenu le", auto_now_add=True)

    class Meta:
        verbose_name = "succes obtenu"
        verbose_name_plural = "succes obtenus"
        ordering = ["-unlocked_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "achievement"],
                name="userachievement_unique_user_achievement",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.achievement}"
