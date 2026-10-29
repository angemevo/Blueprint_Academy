"""Validateur de graphe : E (graphe libre), G (challenge), F (debugging), H (completer).

F et H partent d'un graphe fourni dont certains nodes sont verrouilles.

Soumission : un graphe normalise `{"nodes", "edges", "variables"?}`.
La logique vit dans `services/graph_validation.py`.
"""

from typing import Any

from ..enums import ExerciseType
from ..services.graph_validation import MalformedGraph, check_graph, check_locked_nodes
from .registry import default_registry

START_GRAPH_KEY = {
    ExerciseType.DEBUGGING: "broken_graph",
    ExerciseType.GRAPH_COMPLETE: "partial_graph",
}


@default_registry.register(
    ExerciseType.GRAPH_BUILD,
    ExerciseType.CHALLENGE,
    ExerciseType.DEBUGGING,
    ExerciseType.GRAPH_COMPLETE,
)
class GraphValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        from apps.validation.interfaces import ValidationResult

        try:
            if problems := self._locked_problems(exercise, submission):
                return ValidationResult(is_correct=False, score=0, feedback=problems)
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

    @staticmethod
    def _locked_problems(exercise: Any, submission: Any) -> list[str]:
        key = START_GRAPH_KEY.get(ExerciseType(exercise.type))
        content = exercise.content or {}
        if key is None or not content.get("locked_node_ids"):
            return []
        return check_locked_nodes(content.get(key), content["locked_node_ids"], submission)
