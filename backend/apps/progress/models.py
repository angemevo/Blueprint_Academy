"""Modeles de l'app progress.

Perimetre : LessonProgress, CourseProgress, SkillMastery.

Points structurants (CLAUDE.md) : « lecon terminee » n'est PAS « skill
maitrise ». La completion est un fait binaire (LessonProgress) ; la maitrise est
un score evolutif (SkillMastery), et c'est elle qui ouvre les prerequis.

Surtout : la maitrise ne progresse QUE sur des exercices de PRODUCTION
(`exercises.Exercise.is_practice`). Les echauffements de rappel (types A/B/D) et
la transition (type C) n'y contribuent jamais - « la pratique prime ».
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.enums import CompletionStatus
from common.models import TimeStampedModel


class LessonProgress(TimeStampedModel):
    """Avancement d'un utilisateur sur une lecon."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lesson_progress",
        verbose_name="utilisateur",
    )
    lesson = models.ForeignKey(
        "learning.Lesson",
        on_delete=models.CASCADE,
        related_name="progress_entries",
        verbose_name="lecon",
    )
    status = models.CharField(
        "statut",
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.NOT_STARTED,
        db_index=True,
    )
    started_at = models.DateTimeField("commencee le", null=True, blank=True)
    completed_at = models.DateTimeField("terminee le", null=True, blank=True)
    last_viewed_at = models.DateTimeField("derniere consultation", null=True, blank=True)

    class Meta:
        verbose_name = "progression de lecon"
        verbose_name_plural = "progressions de lecons"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"], name="lessonprogress_unique_user_lesson"
            )
        ]
        indexes = [
            models.Index(fields=["user", "status"], name="lessonprogress_user_st_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.lesson} ({self.get_status_display()})"


class CourseProgress(TimeStampedModel):
    """Avancement d'un utilisateur sur un parcours complet.

    `completion_percent` est un CACHE recalculable a partir des
    `LessonProgress` du parcours ; il n'est ecrit que par la couche service.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="course_progress",
        verbose_name="utilisateur",
    )
    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="progress_entries",
        verbose_name="parcours",
    )
    status = models.CharField(
        "statut",
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.NOT_STARTED,
        db_index=True,
    )
    completion_percent = models.PositiveSmallIntegerField(
        "avancement (%, cache)",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    started_at = models.DateTimeField("commence le", null=True, blank=True)
    completed_at = models.DateTimeField("termine le", null=True, blank=True)

    class Meta:
        verbose_name = "progression de parcours"
        verbose_name_plural = "progressions de parcours"
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "learning_path"],
                name="courseprogress_unique_user_path",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.learning_path} ({self.completion_percent}%)"


class SkillMastery(TimeStampedModel):
    """Maitrise d'un skill par un utilisateur.

    `mastery_score` (0-100) est la mesure qui ouvre les prerequis. Il monte
    avec les reussites sur des exercices de PRODUCTION, redescend avec les
    echecs, et sa regle de calcul vit dans la couche service, jamais ici.
    Un QCM reussi ne le fait pas bouger : c'est la regle centrale du produit.
    """

    #: Seuil a partir duquel un skill est considere comme acquis.
    MASTERED_THRESHOLD = 70

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="skill_masteries",
        verbose_name="utilisateur",
    )
    skill = models.ForeignKey(
        "learning.Skill",
        on_delete=models.CASCADE,
        related_name="masteries",
        verbose_name="skill",
    )
    mastery_score = models.PositiveSmallIntegerField(
        "score de maitrise",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    attempts_count = models.PositiveIntegerField("tentatives", default=0)
    successes_count = models.PositiveIntegerField("reussites", default=0)
    last_practiced_at = models.DateTimeField(
        "derniere pratique", null=True, blank=True
    )

    class Meta:
        verbose_name = "maitrise de skill"
        verbose_name_plural = "maitrises de skills"
        ordering = ["-mastery_score", "skill"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "skill"], name="skillmastery_unique_user_skill"
            )
        ]
        indexes = [
            models.Index(
                fields=["user", "-mastery_score"], name="skillmastery_user_score_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.skill} : {self.mastery_score}"

    @property
    def is_mastered(self) -> bool:
        return self.mastery_score >= self.MASTERED_THRESHOLD
