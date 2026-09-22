"""Enumerations partagees entre plusieurs apps."""

from django.db import models


class Difficulty(models.TextChoices):
    """Niveau de difficulte, commun aux parcours, lecons, exercices, projets."""

    BEGINNER = "beginner", "Debutant"
    INTERMEDIATE = "intermediate", "Intermediaire"
    ADVANCED = "advanced", "Avance"
    EXPERT = "expert", "Expert"


class CompletionStatus(models.TextChoices):
    """Etat d'avancement sur une unite de contenu."""

    NOT_STARTED = "not_started", "Non commence"
    IN_PROGRESS = "in_progress", "En cours"
    COMPLETED = "completed", "Termine"
