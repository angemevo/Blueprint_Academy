"""Validateur des exercices de construction libre : E (graphe libre) et G (challenge).

Soumission : un graphe normalise `{"nodes", "edges", "variables"?}`.
La logique vit dans `services/graph_validation.py`.
"""

from typing import Any

from ..enums import ExerciseType
from ..services.graph_validation import MalformedGraph, check_graph
from .registry import default_registry


@default_registry.register(ExerciseType.GRAPH_BUILD, ExerciseType.CHALLENGE)
class GraphValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        from apps.validation.interfaces import ValidationResult

        try:
            verdict = check_graph(submission, exercise.solution)
        except MalformedGraph:
            return ValidationResult(
                is_correct=False,
                score=0,
                feedback=["Graphe mal formé : envoie des nodes et des connexions."],
            )
        return ValidationResult(
            is_correct=verdict.is_correct, score=verdict.score, feedback=verdict.feedback
        )
