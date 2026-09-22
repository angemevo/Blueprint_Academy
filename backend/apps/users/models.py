"""Modeles de l'app users.

Perimetre : User (modele substituable), role, Profile.

Le role vit sur le User parce qu'il pilote les permissions DRF a chaque
requete ; le Profile porte les donnees pedagogiques et de gamification, dont
le cache denormalise `total_xp` (la source de verite reste le ledger
`gamification.XPTransaction`).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedModel


class Role(models.TextChoices):
    """Roles de la plateforme (voir CLAUDE.md > API REST > Permissions)."""

    STUDENT = "student", "Etudiant"
    INSTRUCTOR = "instructor", "Formateur"
    ADMIN = "admin", "Administrateur"


class User(AbstractUser):
    """Utilisateur de la plateforme."""

    role = models.CharField(
        "role",
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        db_index=True,
    )

    class Meta(AbstractUser.Meta):
        db_table = "users_user"
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"

    @property
    def is_student(self) -> bool:
        return self.role == Role.STUDENT

    @property
    def is_instructor(self) -> bool:
        return self.role == Role.INSTRUCTOR

    @property
    def is_platform_admin(self) -> bool:
        """Role applicatif Admin, distinct du flag Django `is_staff`."""
        return self.role == Role.ADMIN


class Profile(TimeStampedModel):
    """Donnees publiques et de progression d'un utilisateur.

    `total_xp`, `level` et les compteurs de serie sont des CACHES : ils sont
    recalculables a partir de `gamification.XPTransaction`. Ne jamais les
    incrementer ailleurs que dans la couche service dediee.
    """

    user = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="utilisateur",
    )
    display_name = models.CharField("nom affiche", max_length=60, blank=True)
    bio = models.TextField("biographie", max_length=500, blank=True)
    avatar_url = models.URLField("avatar", blank=True)

    total_xp = models.PositiveIntegerField("XP total (cache)", default=0)
    level = models.PositiveSmallIntegerField("niveau (cache)", default=1)

    current_streak = models.PositiveIntegerField("serie en cours", default=0)
    longest_streak = models.PositiveIntegerField("meilleure serie", default=0)
    last_activity_on = models.DateField("derniere activite", null=True, blank=True)

    onboarding_completed = models.BooleanField("onboarding termine", default=False)

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profils"
        indexes = [
            # Sert les classements et le dashboard ; le calcul de reference
            # reste une agregation sur XPTransaction.
            models.Index(fields=["-total_xp"], name="profile_total_xp_desc_idx"),
        ]

    def __str__(self) -> str:
        return f"Profil de {self.user}"
