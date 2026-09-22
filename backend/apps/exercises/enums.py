"""Taxonomie des exercices.

Traduction directe du tableau « Exercices - taxonomie et ponderation » de
CLAUDE.md. Ce module est la SOURCE DE VERITE de la taxonomie : famille, effet
sur la maitrise, schema JSON et validateur en decoulent. Rien ne doit
re-declarer ces listes ailleurs.

Principe directeur : la pratique prime. Le rappel echauffe, la production seule
prouve la maitrise et deverrouille les prerequis.
"""

from django.db import models


class ExerciseType(models.TextChoices):
    """Les 9 types d'exercices du MVP.

    Le code stocke est la lettre (A-I) : stable, court, et directement lisible
    dans les specifications du projet.
    """

    QUESTION = "A", "A - Question"
    MCQ = "B", "B - QCM"
    ORDERING = "C", "C - Remettre dans l'ordre"
    NODE_MATCHING = "D", "D - Node matching"
    GRAPH_BUILD = "E", "E - Construction logique (graphe libre)"
    DEBUGGING = "F", "F - Debugging (corriger un graphe)"
    CHALLENGE = "G", "G - Challenge (objectif a construire)"
    GRAPH_COMPLETE = "H", "H - Completer le graphe"
    UNREAL_EXPORT = "I", "I - Realiser dans Unreal et coller l'export"


class ExerciseFamily(models.TextChoices):
    """Famille pedagogique, qui decide du poids et des effets d'un exercice."""

    RECALL = "recall", "Rappel (echauffement)"
    TRANSITION = "transition", "Transition"
    PRODUCTION = "production", "Production"


#: Famille de chaque type. Table unique, lue partout ailleurs.
TYPE_FAMILIES: dict[str, str] = {
    ExerciseType.QUESTION: ExerciseFamily.RECALL,
    ExerciseType.MCQ: ExerciseFamily.RECALL,
    ExerciseType.NODE_MATCHING: ExerciseFamily.RECALL,
    ExerciseType.ORDERING: ExerciseFamily.TRANSITION,
    ExerciseType.DEBUGGING: ExerciseFamily.PRODUCTION,
    ExerciseType.GRAPH_BUILD: ExerciseFamily.PRODUCTION,
    ExerciseType.CHALLENGE: ExerciseFamily.PRODUCTION,
    ExerciseType.GRAPH_COMPLETE: ExerciseFamily.PRODUCTION,
    ExerciseType.UNREAL_EXPORT: ExerciseFamily.PRODUCTION,
}

#: Types de production : les SEULS qui font progresser `SkillMastery` et
#: deverrouillent des prerequis. C (transition) ne compte pas non plus.
PRODUCTION_TYPES = frozenset(
    code for code, family in TYPE_FAMILIES.items()
    if family == ExerciseFamily.PRODUCTION
)

#: Types de rappel : echauffements courts, XP faible, aucun effet de progression.
RECALL_TYPES = frozenset(
    code for code, family in TYPE_FAMILIES.items()
    if family == ExerciseFamily.RECALL
)

#: Types dont la solution ET la soumission sont un graphe normalise.
#: Le type I passe par le meme moteur, apres normalisation du texte colle
#: depuis Unreal Engine.
GRAPH_BASED_TYPES = frozenset(
    {
        ExerciseType.GRAPH_BUILD,
        ExerciseType.DEBUGGING,
        ExerciseType.CHALLENGE,
        ExerciseType.GRAPH_COMPLETE,
        ExerciseType.UNREAL_EXPORT,
    }
)

#: Production CONTRAINTE : un graphe fourni a completer ou corriger. Peu de
#: solutions valides, donc peu de faux negatifs. CLAUDE.md impose de livrer ces
#: types AVANT le free-build (E/G).
CONSTRAINED_PRODUCTION_TYPES = frozenset(
    {
        ExerciseType.GRAPH_COMPLETE,
        ExerciseType.DEBUGGING,
        ExerciseType.UNREAL_EXPORT,
    }
)

#: Types manipules au glisser-deposer cote frontend (dnd-kit).
DND_BASED_TYPES = frozenset({ExerciseType.ORDERING, ExerciseType.NODE_MATCHING})


def get_family(exercise_type: str) -> str:
    """Famille pedagogique d'un type d'exercice."""
    return TYPE_FAMILIES[exercise_type]


def is_production(exercise_type: str) -> bool:
    """Le type fait-il partie des exercices qui prouvent la maitrise ?"""
    return exercise_type in PRODUCTION_TYPES
