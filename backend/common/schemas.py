"""Contrats JSON partages et helper de validation.

Deux vocabulaires vivent ici :

- le GRAPHE NORMALISE, format pivot de la plateforme. Il sert a l'illustration
  dans les lecons, aux exercices de production (E/F/G/H/I), et sera le format
  cible du collage de nodes exportes depuis Unreal Engine (CLAUDE.md >
  Validation des exercices) ;
- les SELECTEURS, langage dans lequel une solution decrit ce qu'elle exige du
  graphe soumis. Un selecteur decrit une FORME de node ou de connexion, jamais
  une instance precise : c'est ce qui permet de verifier des proprietes sans
  imposer un graphe exact.
"""

from typing import Any

from django.core.exceptions import ValidationError
from jsonschema import Draft202012Validator

_TEXT = {"type": "string", "minLength": 1}


def extend_object(schema: dict[str, Any], **properties: Any) -> dict[str, Any]:
    """Derive un schema d'objet en lui ajoutant des proprietes."""
    return {
        **schema,
        "properties": {**schema["properties"], **properties},
    }


# ---------------------------------------------------------------------------
# Graphe normalise
# ---------------------------------------------------------------------------
# Forme :
#   {"nodes": [{"id", "type"}], "edges": [{"from", "to", "from_pin", "to_pin"}]}
#
# Une connexion Blueprint relie TOUJOURS deux pins nommes : le pin de sortie du
# node amont et le pin d'entree du node aval. Un champ `pin` unique ne pouvait
# pas exprimer, par exemple, que la sortie "True" d'un Branch entre sur le pin
# "exec" d'un Print String. D'ou `from_pin` / `to_pin`, sans equivalent unique.
#
# Les champs supplementaires (label, position) sont optionnels et ne servent
# qu'a l'affichage : la validation ne doit jamais en dependre.

NODE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["id", "type"],
    "properties": {
        "id": _TEXT,
        "type": _TEXT,
        "label": {"type": "string"},
        "position": {
            "type": "object",
            "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
            "required": ["x", "y"],
            "additionalProperties": False,
        },
        # Donnees portees par le node : nom de variable, fonction appelee,
        # classe ciblee, valeur litterale. C'est ce que les selecteurs
        # interrogent via leur champ `match`.
        "properties": {"type": "object"},
    },
    "additionalProperties": False,
}

EDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["from", "to"],
    "properties": {
        "from": _TEXT,
        "to": _TEXT,
        # Pin de sortie du node amont ("exec", "then", "True", "Return Value"...)
        "from_pin": {"type": "string"},
        # Pin d'entree du node aval.
        "to_pin": {"type": "string"},
    },
    "additionalProperties": False,
}

VARIABLE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "name": _TEXT,
        "type": _TEXT,
        "default": {},
    },
    "additionalProperties": False,
}

NORMALIZED_GRAPH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["nodes", "edges"],
    "properties": {
        "nodes": {"type": "array", "items": NODE_SCHEMA},
        "edges": {"type": "array", "items": EDGE_SCHEMA},
        "variables": {"type": "array", "items": VARIABLE_SCHEMA},
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Selecteurs : le langage des exigences
# ---------------------------------------------------------------------------
# Un `type` seul ne suffit pas a designer un node : « un Get » ne dit pas quelle
# variable, « un appel de fonction » ne dit pas laquelle. Le champ `match`
# contraint les donnees du node (`node["properties"]`), sans jamais imposer son
# id ni sa position.
#
# C'est aussi la ou atterrissent les noms CHOISIS par l'auteur du Blueprint
# (variable, evenement personnalise, fonction, macro) : ils n'ont rien a faire
# dans un identifiant de type, sans quoi il faudrait un type par variable de
# chaque projet. Voir `common.blueprint_catalog`.

NODE_MATCH_SCHEMA: dict[str, Any] = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        # Nom de la variable lue ou ecrite (Get / Set).
        "variable": _TEXT,
        # Nom de la fonction appelee, quand elle est definie dans le Blueprint.
        "function": _TEXT,
        # Nom de la macro instanciee, quand elle est definie dans le Blueprint.
        "macro": _TEXT,
        # Nom d'un evenement personnalise.
        "event": _TEXT,
        # Classe ciblee (Cast To, Spawn Actor from Class...).
        "class": _TEXT,
        # Valeur litterale attendue sur une entree.
        "value": {},
    },
    "additionalProperties": False,
}

#: Designe un node par sa forme. Reutilise tel quel aux deux bouts d'une
#: connexion, ce qui garantit un langage unique dans toute la solution.
NODE_SELECTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["type"],
    "properties": {
        "type": _TEXT,
        "match": NODE_MATCH_SCHEMA,
    },
    "additionalProperties": False,
}

#: Designe une connexion entre deux formes de nodes, pins compris.
EDGE_SELECTOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["from", "to"],
    "properties": {
        "from": NODE_SELECTOR_SCHEMA,
        "to": NODE_SELECTOR_SCHEMA,
        "from_pin": {"type": "string"},
        "to_pin": {"type": "string"},
    },
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# Helper de validation
# ---------------------------------------------------------------------------
def error_sort_key(error: Any) -> list[str]:
    """Cle de tri stable pour les erreurs de validation.

    Le chemin d'une erreur melange des cles d'objet (str) et des index de
    tableau (int) ; comparer un int a un str leve un TypeError et ferait
    echouer la validation elle-meme. On trie donc sur la representation
    textuelle de chaque segment.
    """
    return [str(part) for part in error.path]


def validate_against_schema(
    payload: Any, schema: dict[str, Any], *, label: str
) -> None:
    """Valide `payload` et leve une `ValidationError` Django lisible.

    On remonte TOUTES les erreurs d'un coup : un auteur de contenu qui corrige
    son JSON dans l'admin ne doit pas decouvrir les problemes un par un.
    """
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=error_sort_key)
    if not errors:
        return

    messages = []
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "(racine)"
        messages.append(f"{label} > {location} : {error.message}")
    raise ValidationError(messages)
