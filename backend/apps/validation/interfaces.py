"""Contrats de la validation des soumissions (CLAUDE.md, « Validation des exercices »).

Aucun modele, aucune requete, aucun import de `apps.exercises` : l'exercice
est recu tel quel (`Any`), et le validateur concret sait lire son `content` et
sa `solution`.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

#: Bornes du score, en pourcentage de reussite.
MIN_SCORE = 0
MAX_SCORE = 100


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Verdict d'un validateur. Renvoye au client : ne contient jamais la solution.

    `feedback` : messages a montrer a l'eleve ; `hints` : indices apres un echec.
    """

    is_correct: bool
    score: int
    feedback: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # `bool` est un sous-type d'`int` : `True` passerait pour un score de 1.
        if isinstance(self.score, bool) or not isinstance(self.score, int):
            raise TypeError(f"score doit etre un entier, recu {self.score!r}")
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise ValueError(
                f"score doit etre compris entre {MIN_SCORE} et {MAX_SCORE}, recu {self.score}"
            )


@runtime_checkable
class Validator(Protocol):
    """Valide une soumission. Sans etat : une instance sert toutes les soumissions."""

    def validate(self, exercise: Any, submission: Any) -> ValidationResult: ...


class HintService(Protocol):
    """Indices progressifs apres un echec (tuteur IA, V2) : protocole seul au MVP.

    Progression prevue : indice 1, indice 2, explication, puis solution.
    `hints_used` = indices deja consultes (enregistres sur `ExerciseAttempt`).
    Rend `None` quand il n'y a plus rien a proposer. N'est appele qu'apres une
    soumission echouee : seule voie par laquelle la solution atteint le client.
    """

    def next_hint(
        self, exercise: Any, submission: Any, result: ValidationResult, hints_used: int
    ) -> str | None: ...
