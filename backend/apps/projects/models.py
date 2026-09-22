"""Modeles de l'app projects.

Perimetre : Project, ProjectProgress.

Au MVP, un projet se valide par AUTO-DECLARATION guidee (checklist de criteres).
`submission_kind` est le point d'extension prevu pour la V2 : l'utilisateur
collera le texte des nodes exportes depuis Unreal, qui sera normalise en graphe
puis passe au meme moteur de validation que les exercices E/G.
"""

from django.core.exceptions import ValidationError
from django.db import models

from common.content_blocks import validate_content_blocks
from common.enums import CompletionStatus, Difficulty
from common.models import OrderedModel, PublishableModel, TimeStampedModel


class SubmissionKind(models.TextChoices):
    """Mode de validation d'un projet."""

    CHECKLIST = "checklist", "Checklist auto-declaree"
    #: V2 : graphe colle depuis Unreal Engine, valide par proprietes.
    GRAPH = "graph", "Graphe colle (V2)"


class Project(TimeStampedModel, PublishableModel, OrderedModel):
    """Projet a realiser : la derniere marche avant l'autonomie."""

    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug", max_length=200, unique=True)
    summary = models.CharField("resume", max_length=300, blank=True)
    brief = models.JSONField(
        "brief",
        default=dict,
        blank=True,
        help_text='Enonce structure en blocs : {"version": 1, "blocks": [...]}.',
    )
    success_criteria = models.JSONField(
        "criteres de reussite",
        default=list,
        blank=True,
        help_text="Liste de criteres verifiables, presentes en checklist.",
    )

    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.SET_NULL,
        related_name="projects",
        verbose_name="parcours",
        null=True,
        blank=True,
    )
    required_skills = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="unlocks_projects",
        verbose_name="skills prerequis",
    )

    difficulty = models.CharField(
        "difficulte",
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.INTERMEDIATE,
        db_index=True,
    )
    estimated_hours = models.PositiveSmallIntegerField("duree estimee (h)", default=2)
    xp_reward = models.PositiveIntegerField("XP a la completion", default=200)
    submission_kind = models.CharField(
        "mode de validation",
        max_length=20,
        choices=SubmissionKind.choices,
        default=SubmissionKind.CHECKLIST,
    )

    class Meta:
        verbose_name = "projet"
        verbose_name_plural = "projets"
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        try:
            validate_content_blocks(self.brief, label="brief")
        except ValidationError as exc:
            raise ValidationError({"brief": exc.messages}) from exc

    def save(self, *args, **kwargs):
        validate_content_blocks(self.brief, label="brief")
        return super().save(*args, **kwargs)


class ProjectProgress(TimeStampedModel):
    """Avancement d'un utilisateur sur un projet."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="project_progress",
        verbose_name="utilisateur",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="progress_entries",
        verbose_name="projet",
    )
    status = models.CharField(
        "statut",
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.NOT_STARTED,
        db_index=True,
    )
    checklist_state = models.JSONField(
        "etat de la checklist",
        default=dict,
        blank=True,
        help_text="Criteres coches par l'utilisateur, indexes par position.",
    )
    submission = models.JSONField(
        "soumission",
        default=dict,
        blank=True,
        help_text="Vide au MVP ; accueillera le graphe colle en V2.",
    )
    notes = models.TextField("notes personnelles", blank=True)
    started_at = models.DateTimeField("commence le", null=True, blank=True)
    completed_at = models.DateTimeField("termine le", null=True, blank=True)

    class Meta:
        verbose_name = "progression de projet"
        verbose_name_plural = "progressions de projets"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"], name="projectprogress_unique_user_project"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.project} ({self.get_status_display()})"
