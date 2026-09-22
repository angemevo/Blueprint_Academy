"""Modeles de l'app exercises.

Perimetre : Exercise (modele polymorphe unique, types A-I), ExerciseAttempt.

Decisions verrouillees (CLAUDE.md) :

- UN SEUL modele Exercise, pas un par type. Le champ `type` selectionne le
  schema JSON de `content` / `solution`, valide a chaque sauvegarde, et
  selectionnera le validateur de soumission en Phase 2b.
- `is_practice` distingue la PRODUCTION du RAPPEL. Seule la production fait
  progresser la maitrise et deverrouille les prerequis : le champ est derive de
  la taxonomie et verrouille par une contrainte en base, pour qu'aucun contenu
  cree depuis l'admin ne puisse contourner la regle.
- La ponderation XP est CONFIGURABLE (settings.EXERCISE_XP_DEFAULTS), jamais
  ecrite en dur ici.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from common.enums import Difficulty
from common.models import OrderedModel, PublishableModel, TimeStampedModel

from .enums import (
    PRODUCTION_TYPES,
    ExerciseType,
    get_family,
    is_production,
)
from .schemas import validate_exercise_payload

#: Indices progressifs rediges par l'auteur : indice 1, indice 2, explication.
#: Le `HintService` de la V2 (tuteur IA) viendra se brancher sur cette liste.
HINTS_SCHEMA = {
    "type": "array",
    "maxItems": 5,
    "items": {"type": "string", "minLength": 1},
}

_PRODUCTION_CODES = sorted(str(code) for code in PRODUCTION_TYPES)


class Exercise(TimeStampedModel, PublishableModel, OrderedModel):
    """Exercice pratique, rattache ou non a une lecon."""

    lesson = models.ForeignKey(
        "learning.Lesson",
        on_delete=models.CASCADE,
        related_name="exercises",
        verbose_name="lecon",
        null=True,
        blank=True,
        help_text="Vide pour un exercice autonome (challenge, entrainement).",
    )
    type = models.CharField(
        "type",
        max_length=1,
        choices=ExerciseType.choices,
        db_index=True,
    )
    title = models.CharField("titre", max_length=180)
    slug = models.SlugField("slug", max_length=200, unique=True)

    content = models.JSONField(
        "contenu",
        default=dict,
        help_text="Enonce et donnees de l'exercice. Forme imposee par le type.",
    )
    solution = models.JSONField(
        "solution",
        default=dict,
        help_text=(
            "Reponse attendue. Pour les types de production (E/F/G/H/I) : des "
            "PROPRIETES a verifier, jamais un graphe exact."
        ),
    )
    hints = models.JSONField(
        "indices",
        default=list,
        blank=True,
        help_text="Indices progressifs, du plus leger au plus explicite.",
    )

    is_practice = models.BooleanField(
        "exercice de production",
        default=False,
        editable=False,
        db_index=True,
        help_text=(
            "Derive du type. Seuls les exercices de production font progresser "
            "la maitrise et deverrouillent les prerequis."
        ),
    )

    difficulty = models.CharField(
        "difficulte",
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
        db_index=True,
    )
    xp_reward = models.PositiveIntegerField(
        "XP a la reussite",
        null=True,
        blank=True,
        help_text=(
            "Laisser vide pour utiliser la valeur par defaut du type "
            "(settings.EXERCISE_XP_DEFAULTS)."
        ),
    )

    skills = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="practiced_by_exercises",
        verbose_name="skills pratiques",
    )
    required_skills = models.ManyToManyField(
        "learning.Skill",
        blank=True,
        related_name="unlocks_exercises",
        verbose_name="skills prerequis",
    )

    # --- Flags de challenge (type G). La vraie entite Challenge arrive en V3.
    time_limit_seconds = models.PositiveIntegerField(
        "limite de temps (s)", null=True, blank=True
    )
    max_attempts = models.PositiveSmallIntegerField(
        "essais maximum", null=True, blank=True
    )
    is_featured = models.BooleanField("mis en avant", default=False)

    class Meta:
        verbose_name = "exercice"
        verbose_name_plural = "exercices"
        ordering = ["lesson", "order", "title"]
        constraints = [
            # Verrou de la regle pedagogique centrale : seul un type de
            # production peut compter comme pratique, et il compte toujours.
            models.CheckConstraint(
                condition=(
                    models.Q(is_practice=True, type__in=_PRODUCTION_CODES)
                    | models.Q(is_practice=False)
                    & ~models.Q(type__in=_PRODUCTION_CODES)
                ),
                name="exercise_is_practice_matches_taxonomy",
            )
        ]
        indexes = [
            models.Index(fields=["type", "is_published"], name="exercise_type_pub_idx"),
            models.Index(
                fields=["is_practice", "is_published"], name="exercise_practice_idx"
            ),
        ]

    def __str__(self) -> str:
        return f"[{self.type}] {self.title}"

    # -- Taxonomie -----------------------------------------------------------
    @property
    def family(self) -> str:
        """Famille pedagogique : rappel, transition ou production."""
        return get_family(self.type)

    @property
    def is_challenge(self) -> bool:
        return self.type == ExerciseType.CHALLENGE

    @property
    def effective_xp_reward(self) -> int:
        """XP reellement attribuee : surcharge de l'exercice, sinon le defaut du type."""
        if self.xp_reward is not None:
            return self.xp_reward
        return settings.EXERCISE_XP_DEFAULTS.get(
            self.type, settings.EXERCISE_XP_FALLBACK
        )

    # -- Validation ----------------------------------------------------------
    def clean(self) -> None:
        super().clean()
        validate_exercise_payload(self.type, self.content, self.solution)
        self._validate_hints()

    def save(self, *args, **kwargs):
        # Valide quelle que soit la porte d'entree : admin, API, seed, shell.
        validate_exercise_payload(self.type, self.content, self.solution)
        self._validate_hints()
        # La taxonomie est la source de verite : le champ n'est qu'un cache
        # indexable, jamais une decision d'auteur.
        self.is_practice = is_production(self.type)
        return super().save(*args, **kwargs)

    def _validate_hints(self) -> None:
        from common.schemas import validate_against_schema

        try:
            validate_against_schema(self.hints or [], HINTS_SCHEMA, label="indices")
        except ValidationError as exc:
            raise ValidationError({"hints": exc.messages}) from exc


class ExerciseAttempt(TimeStampedModel):
    """Tentative de resolution.

    Chaque soumission est conservee : c'est la matiere premiere de la maitrise
    (`progress.SkillMastery`), des statistiques et, en V2, du tuteur IA.
    """

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="exercise_attempts",
        verbose_name="utilisateur",
    )
    exercise = models.ForeignKey(
        "exercises.Exercise",
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="exercice",
    )
    attempt_number = models.PositiveIntegerField("numero de tentative", default=1)

    submission = models.JSONField(
        "soumission",
        default=dict,
        help_text=(
            "Pour les types de production : un graphe normalise. Pour le type I, "
            "le texte colle depuis Unreal est normalise avant d'etre stocke."
        ),
    )
    raw_submission = models.TextField(
        "soumission brute",
        blank=True,
        help_text="Texte d'origine colle par l'utilisateur (type I), pour audit.",
    )
    is_correct = models.BooleanField("reussie", default=False)
    score = models.PositiveSmallIntegerField(
        "score",
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 a 100. Un exercice peut etre partiellement juste.",
    )
    feedback = models.JSONField(
        "retour",
        default=dict,
        blank=True,
        help_text="ValidationResult serialise : messages, indices declenches.",
    )
    hints_used = models.PositiveSmallIntegerField("indices consultes", default=0)
    duration_seconds = models.PositiveIntegerField("duree (s)", null=True, blank=True)

    class Meta:
        verbose_name = "tentative"
        verbose_name_plural = "tentatives"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "exercise", "attempt_number"],
                name="attempt_unique_number_per_user_exercise",
            )
        ]
        indexes = [
            models.Index(
                fields=["user", "exercise", "-created_at"], name="attempt_user_ex_idx"
            ),
            models.Index(
                fields=["exercise", "is_correct"], name="attempt_exercise_ok_idx"
            ),
        ]

    def __str__(self) -> str:
        issue = "reussie" if self.is_correct else "echouee"
        return (
            f"{self.user} - {self.exercise} (tentative {self.attempt_number}, {issue})"
        )
