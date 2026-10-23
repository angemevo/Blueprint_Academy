"""Validateurs des types de rappel et de transition : A, B, C, D.

Formats de soumission (cote client) :
- A : {"answer": "texte"}
- B : {"selected_option_ids": ["id", ...]}
- C : {"order": ["id", ...]}
- D : {"pairs": [{"left_id": "id", "right_id": "id"}, ...]}

Bareme : A/B tout-ou-rien ; C = part des elements a la bonne position ;
D = part des paires correctes. `is_correct` n'est vrai qu'a 100.
Le feedback ne cite jamais la solution ni l'`explanation` de l'auteur ; seules
les `option_explanations` (B), ecrites pour les options cochees a tort, sont
renvoyees.
L'import de `apps.validation` reste local aux fonctions.
"""

from typing import Any

from ..enums import ExerciseType
from .registry import default_registry

MAX_SCORE = 100
_MALFORMED = "Réponse mal formée : il manque un élément ou son format est invalide."


def _result(score: int, feedback: list[str]) -> Any:
    from apps.validation.interfaces import ValidationResult

    return ValidationResult(is_correct=score == MAX_SCORE, score=score, feedback=feedback)


def _malformed(detail: str = _MALFORMED) -> Any:
    return _result(0, [detail])


def _field(submission: Any, key: str) -> Any:
    return submission.get(key) if isinstance(submission, dict) else None


def _is_id_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _normalize(text: str, case_sensitive: bool) -> str:
    collapsed = " ".join(text.split())
    return collapsed if case_sensitive else collapsed.casefold()


@default_registry.register(ExerciseType.QUESTION)
class QuestionValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        answer = _field(submission, "answer")
        if not isinstance(answer, str) or not answer.strip():
            return _malformed("Écris une réponse avant de valider.")
        solution = exercise.solution
        case_sensitive = bool(solution.get("case_sensitive", False))
        given = _normalize(answer, case_sensitive)
        accepted = {_normalize(a, case_sensitive) for a in solution["accepted_answers"]}
        if given in accepted:
            return _result(MAX_SCORE, ["Bonne réponse."])
        return _result(0, ["Ce n'est pas la bonne réponse."])


@default_registry.register(ExerciseType.MCQ)
class MCQValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        selected = _field(submission, "selected_option_ids")
        if not _is_id_list(selected) or not selected:
            return _malformed("Choisis au moins une option avant de valider.")
        known = {o["id"] for o in exercise.content.get("options", [])}
        if len(set(selected)) != len(selected) or not set(selected) <= known:
            return _malformed("Une option choisie n'existe pas dans cette question.")
        solution = exercise.solution
        if set(selected) == set(solution["correct_option_ids"]):
            return _result(MAX_SCORE, ["Bonne réponse."])
        feedback = ["Ce n'est pas la bonne réponse."]
        per_option = solution.get("option_explanations", {})
        feedback += [per_option[i] for i in selected if i in per_option]
        return _result(0, feedback)


@default_registry.register(ExerciseType.ORDERING)
class OrderingValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        order = _field(submission, "order")
        known = [i["id"] for i in exercise.content.get("items", [])]
        if not _is_id_list(order) or sorted(order) != sorted(known):
            return _malformed("Place chaque élément exactement une fois.")
        expected = exercise.solution["order"]
        placed = sum(1 for given, want in zip(order, expected, strict=False) if given == want)
        score = placed * MAX_SCORE // len(expected)
        if score == MAX_SCORE:
            return _result(MAX_SCORE, ["Ordre correct."])
        return _result(score, [f"{placed} élément(s) sur {len(expected)} bien placé(s)."])


@default_registry.register(ExerciseType.NODE_MATCHING)
class NodeMatchingValidator:
    def validate(self, exercise: Any, submission: Any) -> Any:
        pairs = _field(submission, "pairs")
        if not isinstance(pairs, list) or not pairs:
            return _malformed("Associe au moins un élément avant de valider.")
        left = {i["id"] for i in exercise.content.get("left", [])}
        right = {i["id"] for i in exercise.content.get("right", [])}
        given: set[tuple[str, str]] = set()
        for pair in pairs:
            lid, rid = _field(pair, "left_id"), _field(pair, "right_id")
            if lid not in left or rid not in right:
                return _malformed("Une association utilise un élément inconnu.")
            given.add((lid, rid))
        expected = {(p["left_id"], p["right_id"]) for p in exercise.solution["pairs"]}
        found = len(given & expected)
        score = found * MAX_SCORE // len(expected)
        if score == MAX_SCORE and given == expected:
            return _result(MAX_SCORE, ["Toutes les associations sont correctes."])
        score = min(score, MAX_SCORE - 1) if given != expected else score
        return _result(score, [f"{found} association(s) correcte(s) sur {len(expected)}."])
