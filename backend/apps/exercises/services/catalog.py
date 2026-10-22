"""Lecture des exercices pour les clients : visibilite et mise en forme publique.

La `solution` et le texte des `hints` ne sortent jamais d'ici : les indices
seront servis un par un par le futur `HintService`.
"""

import random
from copy import deepcopy

from django.db.models import Q

from apps.exercises.enums import ExerciseType
from apps.exercises.models import Exercise
from apps.learning.services.catalog import can_see_unpublished


def exercises_queryset(user):
    """Exercices visibles ; non publie si sa lecon, son module ou son parcours ne l'est pas."""
    qs = Exercise.objects.select_related("lesson")
    if not can_see_unpublished(user):
        qs = qs.filter(is_published=True).filter(
            Q(lesson__isnull=True)
            | Q(
                lesson__is_published=True,
                lesson__module__is_published=True,
                lesson__module__learning_path__is_published=True,
            )
        )
    return qs


def lesson_exercises(lesson, user):
    """Exercices d'une lecon, visibles par `user` (titre, type, id seulement)."""
    qs = lesson.exercises.all()
    if not can_see_unpublished(user):
        qs = qs.filter(is_published=True)
    return qs.only("id", "title", "type", "order", "lesson_id").order_by("order", "title")


def shuffle_ordering_items(items: list, solution_order: list, rng=random) -> list:
    """Melange les elements du type C sans jamais renvoyer l'ordre de la solution.

    Avec au moins 2 elements, un ordre different est garanti (rotation en
    dernier recours).
    """
    shuffled = list(items)
    if len(shuffled) < 2:
        return shuffled
    for _ in range(10):
        rng.shuffle(shuffled)
        if [i["id"] for i in shuffled] != list(solution_order):
            return shuffled
    rotated = shuffled[1:] + shuffled[:1]
    if [i["id"] for i in rotated] != list(solution_order):
        return rotated
    return shuffled[::-1]


def public_content(exercise: Exercise) -> dict:
    """Contenu destine au client ; le type C est melange a chaque appel."""
    content = deepcopy(exercise.content)
    if exercise.type == ExerciseType.ORDERING:
        content["items"] = shuffle_ordering_items(
            content.get("items", []), exercise.solution.get("order", [])
        )
    return content
