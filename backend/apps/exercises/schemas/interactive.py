"""Schemas des exercices de rappel et de transition : types A, B, C, D.

Ces types sont des ECHAUFFEMENTS (CLAUDE.md > taxonomie) : courts, XP faible,
sans effet sur la maitrise. Ils peuvent afficher un graphe en illustration,
mais l'utilisateur n'y construit rien - c'est ce qui les distingue des types de
production E/F/G/H/I.
"""

from typing import Any

from common.schemas import NORMALIZED_GRAPH_SCHEMA

_ID = {"type": "string", "minLength": 1}
_TEXT = {"type": "string", "minLength": 1}
_ID_LIST = {"type": "array", "minItems": 1, "items": _ID, "uniqueItems": True}

#: Graphe purement illustratif, commun aux types de rappel : « regarde ce
#: graphe, puis reponds ». Optionnel.
_ILLUSTRATION = {
    "graph": NORMALIZED_GRAPH_SCHEMA,
    "graph_caption": {"type": "string"},
}


# ---------------------------------------------------------------------------
# A - Question (reponse courte en saisie libre)
# ---------------------------------------------------------------------------
QUESTION_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["question"],
    "properties": {
        "question": _TEXT,
        "placeholder": {"type": "string"},
        # Pas d'indice ici : les indices progressifs vivent sur `Exercise.hints`,
        # pour tous les types a la fois, et c'est la que se branchera le
        # HintService du tuteur IA (V2).
        **_ILLUSTRATION,
    },
    "additionalProperties": False,
}

QUESTION_SOLUTION: dict[str, Any] = {
    "type": "object",
    "required": ["accepted_answers"],
    "properties": {
        # Plusieurs formulations valides : "BeginPlay", "Begin Play", "Event BeginPlay".
        "accepted_answers": {"type": "array", "minItems": 1, "items": _TEXT},
        "case_sensitive": {"type": "boolean"},
        "explanation": {"type": "string"},
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# B - QCM
# ---------------------------------------------------------------------------
MCQ_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["question", "options"],
    "properties": {
        "question": _TEXT,
        "options": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["id", "text"],
                "properties": {
                    "id": _ID,
                    "text": _TEXT,
                    "image_url": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "multiple": {"type": "boolean"},
        "shuffle": {"type": "boolean"},
        **_ILLUSTRATION,
    },
    "additionalProperties": False,
}

MCQ_SOLUTION: dict[str, Any] = {
    "type": "object",
    "required": ["correct_option_ids"],
    "properties": {
        "correct_option_ids": _ID_LIST,
        "explanation": {"type": "string"},
        # Retour cible par option cochee a tort : le coeur de la pedagogie.
        "option_explanations": {
            "type": "object",
            "additionalProperties": {"type": "string"},
        },
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# C - Remettre dans l'ordre (glisser-deposer)
# ---------------------------------------------------------------------------
# Famille « transition » : l'utilisateur raisonne sur un enchainement
# d'execution sans encore construire. XP moyen, mais aucun effet de maitrise.
ORDERING_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["items"],
    "properties": {
        "prompt": {"type": "string"},
        "items": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": _ID,
                    "label": _TEXT,
                    "node_type": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        **_ILLUSTRATION,
    },
    "additionalProperties": False,
}

ORDERING_SOLUTION: dict[str, Any] = {
    "type": "object",
    "required": ["order"],
    "properties": {
        "order": _ID_LIST,
        "explanation": {"type": "string"},
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# D - Node matching (glisser-deposer)
# ---------------------------------------------------------------------------
# Associer un node a son role, sa categorie ou sa sortie.
NODE_MATCHING_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["left", "right"],
    "properties": {
        "prompt": {"type": "string"},
        "left": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {
                    "id": _ID,
                    "label": _TEXT,
                    # Permet d'afficher la vignette du node plutot qu'un texte.
                    "node_type": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "right": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["id", "label"],
                "properties": {"id": _ID, "label": _TEXT},
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

NODE_MATCHING_SOLUTION: dict[str, Any] = {
    "type": "object",
    "required": ["pairs"],
    "properties": {
        "pairs": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["left_id", "right_id"],
                "properties": {"left_id": _ID, "right_id": _ID},
                "additionalProperties": False,
            },
        },
        "explanation": {"type": "string"},
    },
    "additionalProperties": False,
}
