"""Vocabulaire des blocs de contenu redactionnel.

Partage par les lecons (`learning.Lesson.content`) et les briefs de projets
(`projects.Project.brief`) : meme grammaire de blocs, donc meme schema, donc un
seul rendu a ecrire cote frontend.

Les variantes de callout reprennent les questions pedagogiques imposees par
CLAUDE.md (pourquoi, quand, erreur du debutant, usage dans un vrai jeu).
"""


from typing import Any

from django.core.exceptions import ValidationError

from common.blueprint_catalog import is_known_node_type
from common.schemas import NORMALIZED_GRAPH_SCHEMA, validate_against_schema

CALLOUT_VARIANTS = [
    "info",  # Qu'est-ce que c'est
    "why",  # Pourquoi ca existe
    "when",  # Quand l'utiliser
    "tip",  # Astuce
    "pitfall",  # Erreur classique du debutant
    "real_game",  # Usage dans un vrai jeu
]

_BLOCK_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "object",
        "required": ["type", "text"],
        "properties": {
            "type": {"const": "heading"},
            "text": {"type": "string", "minLength": 1},
            "level": {"type": "integer", "minimum": 2, "maximum": 4},
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "text"],
        "properties": {
            "type": {"const": "text"},
            "text": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "items"],
        "properties": {
            "type": {"const": "list"},
            "style": {"enum": ["bullet", "numbered"]},
            "items": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "code"],
        "properties": {
            "type": {"const": "code"},
            "language": {"type": "string"},
            "code": {"type": "string", "minLength": 1},
            "caption": {"type": "string"},
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "text"],
        "properties": {
            "type": {"const": "callout"},
            "variant": {"enum": CALLOUT_VARIANTS},
            "title": {"type": "string"},
            "text": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "url"],
        "properties": {
            "type": {"const": "image"},
            "url": {"type": "string", "minLength": 1},
            "alt": {"type": "string"},
            "caption": {"type": "string"},
        },
        "additionalProperties": False,
    },
    {
        # Illustration d'un graphe de nodes, au format pivot de la plateforme.
        "type": "object",
        "required": ["type", "graph"],
        "properties": {
            "type": {"const": "graph"},
            "graph": NORMALIZED_GRAPH_SCHEMA,
            "caption": {"type": "string"},
        },
        "additionalProperties": False,
    },
    {
        "type": "object",
        "required": ["type", "items"],
        "properties": {
            "type": {"const": "key_points"},
            "title": {"type": "string"},
            "items": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string", "minLength": 1},
            },
        },
        "additionalProperties": False,
    },
    {
        # Question de verification sans notation, pour casser les longs blocs.
        "type": "object",
        "required": ["type", "question", "answer"],
        "properties": {
            "type": {"const": "self_check"},
            "question": {"type": "string", "minLength": 1},
            "answer": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
    },
]

BLOCK_TYPES = [schema["properties"]["type"]["const"] for schema in _BLOCK_SCHEMAS]

CONTENT_BLOCKS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["blocks"],
    "properties": {
        "version": {"type": "integer", "minimum": 1},
        "blocks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["type"],
                "properties": {"type": {"enum": BLOCK_TYPES}},
                "allOf": [
                    {
                        "if": {"properties": {"type": {"const": block_type}}},
                        "then": block_schema,
                    }
                    for block_type, block_schema in zip(BLOCK_TYPES, _BLOCK_SCHEMAS)
                ],
            },
        },
    },
    "additionalProperties": False,
}


def validate_content_blocks(content, *, label: str = "contenu") -> None:
    """Valide un document de blocs. Un document vide est accepte (redaction a venir)."""
    if not content:
        return
    validate_against_schema(content, CONTENT_BLOCKS_SCHEMA, label=label)
    _validate_graph_blocks_vocabulary(content, label=label)


def _validate_graph_blocks_vocabulary(content: dict, *, label: str) -> None:
    """Un graphe illustre dans une lecon parle le meme vocabulaire que le reste.

    Le catalogue est unique pour toute la plateforme (CLAUDE.md) : une lecon qui
    dessine un node inexistant enseigne un nom faux, exactement comme un
    exercice qui l'exigerait.
    """
    unknown: set[str] = set()
    for index, block in enumerate(content.get("blocks", [])):
        if not isinstance(block, dict) or block.get("type") != "graph":
            continue
        for node in block.get("graph", {}).get("nodes", []):
            node_type = node.get("type") if isinstance(node, dict) else None
            if node_type and not is_known_node_type(node_type):
                unknown.add(f"bloc {index} : {node_type}")
    if unknown:
        raise ValidationError(
            f"{label} : types de nodes absents du catalogue ({sorted(unknown)}). "
            "Verifier l'identifiant dans l'export UE5, ou completer le catalogue "
            "via le reglage BLUEPRINT_EXTRA_NODE_TYPES."
        )
