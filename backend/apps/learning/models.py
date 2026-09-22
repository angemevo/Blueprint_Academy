"""Modeles de l'app learning.

Perimetre : Skill, LearningPath, Module, Lesson.

Point structurant (CLAUDE.md) : `Skill` est une entite de premier ordre,
ORTHOGONALE a Path/Module/Lesson. Une lecon enseigne des skills, et les
prerequis se declarent en skills, jamais en lecons.
"""

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from common.enums import Difficulty
from common.models import OrderedModel, PublishableModel, TimeStampedModel

from .schemas import validate_lesson_content


class SkillCategory(models.TextChoices):
    """Familles de concepts Blueprint, pour l'organisation et les filtres."""

    FUNDAMENTALS = "fundamentals", "Fondamentaux"
    VARIABLES = "variables", "Variables et types"
    FLOW_CONTROL = "flow_control", "Controle de flux"
    FUNCTIONS = "functions", "Fonctions et macros"
    OOP = "oop", "Classes, heritage, interfaces"
    ACTORS = "actors", "Acteurs et composants"
    INPUT = "input", "Entrees joueur"
    UI = "ui", "Interface (UMG)"
    GAMEPLAY = "gameplay", "Systemes de gameplay"
    AI = "ai", "Intelligence artificielle"
    PHYSICS = "physics", "Physique et collisions"
    DEBUGGING = "debugging", "Debogage"
    OPTIMIZATION = "optimization", "Optimisation"


class Skill(TimeStampedModel):
    """Concept Blueprint maitrisable, unite de prerequis de la plateforme."""

    name = models.CharField("nom", max_length=120, unique=True)
    slug = models.SlugField("slug", max_length=140, unique=True)
    description = models.TextField("description", blank=True)
    category = models.CharField(
        "categorie",
        max_length=30,
        choices=SkillCategory.choices,
        default=SkillCategory.FUNDAMENTALS,
        db_index=True,
    )
    difficulty = models.CharField(
        "difficulte",
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
        db_index=True,
    )
    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="unlocks",
        verbose_name="prerequis",
        help_text="Skills a maitriser avant d'aborder celui-ci.",
    )
    is_active = models.BooleanField("actif", default=True)

    class Meta:
        verbose_name = "skill"
        verbose_name_plural = "skills"
        ordering = ["category", "difficulty", "name"]

    def __str__(self) -> str:
        return self.name


class LearningPath(TimeStampedModel, PublishableModel, OrderedModel):
    """Parcours : la plus grande unite de contenu (ex. Blueprint Fundamentals)."""

    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug", max_length=200, unique=True)
    subtitle = models.CharField("sous-titre", max_length=250, blank=True)
    description = models.TextField("description", blank=True)
    difficulty = models.CharField(
        "difficulte",
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
        db_index=True,
    )
    estimated_hours = models.PositiveSmallIntegerField("duree estimee (h)", default=0)
    cover_image_url = models.URLField("image de couverture", blank=True)
    required_skills = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="unlocks_paths",
        verbose_name="skills prerequis",
    )

    class Meta:
        verbose_name = "parcours"
        verbose_name_plural = "parcours"
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title


class Module(TimeStampedModel, PublishableModel, OrderedModel):
    """Chapitre d'un parcours, regroupant des lecons."""

    learning_path = models.ForeignKey(
        "learning.LearningPath",
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="parcours",
    )
    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug", max_length=200)
    description = models.TextField("description", blank=True)

    class Meta:
        verbose_name = "module"
        verbose_name_plural = "modules"
        ordering = ["learning_path", "order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["learning_path", "slug"], name="module_unique_slug_per_path"
            )
        ]

    def __str__(self) -> str:
        return f"{self.learning_path.title} / {self.title}"


class Lesson(TimeStampedModel, PublishableModel, OrderedModel):
    """Lecon : contenu pedagogique structure en blocs JSON.

    Le contenu n'est jamais du texte libre : il est decoupe en blocs valides
    par `schemas.validate_lesson_content`, ce qui permet au frontend de rendre
    chaque type de bloc et a l'admin de creer du contenu sans toucher au code.
    """

    module = models.ForeignKey(
        "learning.Module",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="module",
    )
    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug", max_length=200)
    summary = models.CharField("resume", max_length=300, blank=True)
    content = models.JSONField(
        "contenu",
        default=dict,
        blank=True,
        help_text='Structure : {"version": 1, "blocks": [...]}.',
    )
    estimated_minutes = models.PositiveSmallIntegerField(
        "duree estimee (min)", default=10, validators=[MinValueValidator(1)]
    )
    xp_reward = models.PositiveIntegerField("XP a la completion", default=10)

    skills_taught = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="taught_by_lessons",
        verbose_name="skills enseignes",
    )
    required_skills = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="unlocks_lessons",
        verbose_name="skills prerequis",
        help_text="Prerequis exprimes en skills, jamais en lecons.",
    )

    class Meta:
        verbose_name = "lecon"
        verbose_name_plural = "lecons"
        ordering = ["module", "order", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "slug"], name="lesson_unique_slug_per_module"
            )
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        super().clean()
        try:
            validate_lesson_content(self.content)
        except ValidationError as exc:
            raise ValidationError({"content": exc.messages}) from exc

    def save(self, *args, **kwargs):
        # Le contenu est valide a la sauvegarde, quelle que soit la porte
        # d'entree : admin, API, shell ou commande de seed.
        validate_lesson_content(self.content)
        return super().save(*args, **kwargs)
