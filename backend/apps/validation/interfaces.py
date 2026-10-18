"""Contrats de la validation des soumissions (CLAUDE.md, « Validation des exercices »).

- `ValidationResult` : ce que tout validateur rend, quel que soit le type ;
- `Validator` : l'interface `validate(exercise, submission) -> ValidationResult` ;
- `HintService` : la prise ou se branchera le tuteur IA (V2). Protocole seul,
  aucune implementation au MVP.

Ce module ne declare aucun modele et n'execute aucune requete. Il n'importe rien
de `apps.exercises` non plus : l'exercice est recu tel quel (`Any`), et c'est au
validateur concret de savoir lire son `content` et sa `solution`.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

#: Bornes du score, en pourcentage de reussite.
MIN_SCORE = 0
MAX_SCORE = 100


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Verdict d'un validateur sur une soumission.

    - `is_correct` : la soumission est acceptee ;
    - `score` : entier de 0 a 100, borne verifiee a la construction ;
    - `feedback` : messages a montrer a l'eleve, dans l'ordre ;
    - `hints` : indices proposes apres un echec.

    Le resultat ne contient jamais la `solution` : il est renvoye au client.
    """

    is_correct: bool
    score: int
    feedback: list[str] = field(default_factory=list)
    hints: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # `bool` est un sous-type d'`int` : `True` passerait pour un score de 1.
        if isinstance(self.score, bool) or not isinstance(self.score, int):
            raise TypeError(
                f"score doit etre un entier, recu {type(self.score).__name__} ({self.score!r})"
            )
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise ValueError(
                f"score doit etre compris entre {MIN_SCORE} et {MAX_SCORE}, recu {self.score}"
            )


@runtime_checkable
class Validator(Protocol):
    """Valide la soumission d'un eleve pour un exercice donne.

    Un validateur est sans etat : une seule instance sert toutes les
    soumissions du ou des types pour lesquels il est enregistre.
    """

    def validate(self, exercise: Any, submission: Any) -> ValidationResult: ...


class HintService(Protocol):
    """Indices progressifs apres un echec (tuteur IA, V2).

    Progression prevue par CLAUDE.md : indice 1, indice 2, explication, puis
    solution. `hints_used` est le nombre d'indices deja consultes pour cet
    exercice, tel qu'enregistre sur `ExerciseAttempt`. La reponse est `None`
    quand il n'y a plus rien a proposer.

    Ne s'appelle qu'apres une soumission echouee : c'est la seule voie par
    laquelle la solution peut atteindre le client.
    """

    def next_hint(
        self,
        exercise: Any,
        submission: Any,
        result: ValidationResult,
        hints_used: int,
    ) -> str | None: ...
