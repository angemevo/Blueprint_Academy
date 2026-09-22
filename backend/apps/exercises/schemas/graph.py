"""Schemas des exercices de PRODUCTION : types E, F, G, H, I.

Ce sont les exercices qui comptent (CLAUDE.md > taxonomie) : ils font
progresser la maitrise et deverrouillent les prerequis. Tous partagent :

- une soumission au format GRAPHE NORMALISE (pour I, apres normalisation du
  texte colle depuis Unreal Engine) ;
- une solution exprimee en PROPRIETES a verifier - jamais un graphe exact. Un
  enonce a toujours plusieurs implementations valides ; une comparaison stricte
  produirait des faux negatifs.

Les exigences s'ecrivent avec les SELECTEURS de `common.schemas` : un selecteur
decrit la forme d'un node (`type`, plus un `match` optionnel sur la variable,
la fonction ou la classe visee), et une connexion se decrit par deux selecteurs
et les pins concernes. Meme langage des deux cotes d'une connexion, meme
langage pour ce qui est requis et pour ce qui est interdit.

Les types contraints (H completer, F corriger, I reproduire) fournissent deja
un graphe : l'espace des solutions y est etroit, donc le risque de faux negatif
est faible. C'est la raison pour laquelle CLAUDE.md impose de les livrer avant
le free-build (E/G).
"""

from typing import Any

from common.schemas import (
    EDGE_SELECTOR_SCHEMA,
    NODE_SELECTOR_SCHEMA,
    NORMALIZED_GRAPH_SCHEMA,
    VARIABLE_SCHEMA,
    extend_object,
)

_ID = {"type": "string", "minLength": 1}
_TEXT = {"type": "string", "minLength": 1}

#: Message affiche a l'eleve quand l'exigence n'est pas satisfaite.
_FEEDBACK = {"type": "string"}

#: Entree de palette : un type de node que l'utilisateur peut poser.
#: Seul l'identifiant de catalogue est requis ; le libelle affiche vient du
#: catalogue, pour qu'aucun enonce ne puisse renommer un node d'Unreal.
_PALETTE_ITEM: dict[str, Any] = {
    "type": "object",
    "required": ["type"],
    "properties": {
        "type": _TEXT,
        "label": _TEXT,
        "category": {"type": "string"},
        "description": {"type": "string"},
    },
    "additionalProperties": False,
}

_PALETTE = {"type": "array", "minItems": 1, "items": _PALETTE_ITEM}

# --- Exigences, derivees des selecteurs partages ----------------------------
_REQUIRED_NODE = extend_object(
    NODE_SELECTOR_SCHEMA,
    min_count={"type": "integer", "minimum": 1},
    feedback=_FEEDBACK,
)
_FORBIDDEN_NODE = extend_object(NODE_SELECTOR_SCHEMA, feedback=_FEEDBACK)
_REQUIRED_EDGE = extend_object(EDGE_SELECTOR_SCHEMA, feedback=_FEEDBACK)
_FORBIDDEN_EDGE = extend_object(EDGE_SELECTOR_SCHEMA, feedback=_FEEDBACK)


# ---------------------------------------------------------------------------
# Solution par proprietes, partagee par TOUS les types de production
# ---------------------------------------------------------------------------
GRAPH_REQUIREMENTS_SOLUTION: dict[str, Any] = {
    "type": "object",
    "properties": {
        # `minItems` n'est pas cosmetique : sans lui, `{"required_nodes": []}`
        # satisferait le `anyOf` ci-dessous tout en n'exigeant rien, et une
        # soumission vide reussirait l'exercice.
        "required_nodes": {"type": "array", "minItems": 1, "items": _REQUIRED_NODE},
        "required_edges": {"type": "array", "minItems": 1, "items": _REQUIRED_EDGE},
        "required_variables": {
            "type": "array",
            "minItems": 1,
            "items": VARIABLE_SCHEMA,
        },
        "forbidden_nodes": {
            "type": "array",
            "minItems": 1,
            "items": _FORBIDDEN_NODE,
        },
        # Utile aux types F et H : la connexion fautive doit avoir disparu.
        "forbidden_edges": {
            "type": "array",
            "minItems": 1,
            "items": _FORBIDDEN_EDGE,
        },
        "max_nodes": {"type": "integer", "minimum": 1},
        # Graphe indicatif, purement informatif (correction, indices).
        # Il n'est JAMAIS compare a la soumission.
        "reference_graph": NORMALIZED_GRAPH_SCHEMA,
        "explanation": {"type": "string"},
    },
    # Tout type de production exige au moins une clause POSITIVE : sans elle,
    # un graphe vide passerait (les clauses forbidden_* sont satisfaites par
    # l'absence de tout). Elles completent une exigence, ne la remplacent pas.
    "anyOf": [
        {"required": ["required_nodes"]},
        {"required": ["required_edges"]},
        {"required": ["required_variables"]},
    ],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------------
# E - Construction logique (graphe libre)
# ---------------------------------------------------------------------------
GRAPH_BUILD_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["prompt", "palette"],
    "properties": {
        "prompt": _TEXT,
        "palette": _PALETTE,
        # Canvas de depart, generalement vide ou reduit a l'evenement d'entree.
        "initial_graph": NORMALIZED_GRAPH_SCHEMA,
        "variables": {"type": "array", "items": VARIABLE_SCHEMA},
        "notes": {"type": "string"},
    },
    "additionalProperties": False,
}

GRAPH_BUILD_SOLUTION = GRAPH_REQUIREMENTS_SOLUTION


# ---------------------------------------------------------------------------
# F - Debugging : corriger un graphe casse
# ---------------------------------------------------------------------------
DEBUGGING_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["prompt", "broken_graph"],
    "properties": {
        "prompt": _TEXT,
        # Le graphe fautif, pose sur le canvas. L'utilisateur le REPARE.
        "broken_graph": NORMALIZED_GRAPH_SCHEMA,
        # Symptome observe en jeu : c'est le point de depart du raisonnement.
        "symptom": {"type": "string"},
        # Palette optionnelle : certains bugs se corrigent en ajoutant un node.
        "palette": {"type": "array", "items": _PALETTE_ITEM},
        "variables": {"type": "array", "items": VARIABLE_SCHEMA},
        # Nodes que l'utilisateur ne peut ni deplacer ni supprimer.
        "locked_node_ids": {"type": "array", "items": _ID},
    },
    "additionalProperties": False,
}

DEBUGGING_SOLUTION = GRAPH_REQUIREMENTS_SOLUTION


# ---------------------------------------------------------------------------
# G - Challenge : un objectif, a construire
# ---------------------------------------------------------------------------
# Les flags (chrono, nombre d'essais) vivent sur le modele, pas dans le
# contenu : la vraie entite Challenge n'arrive qu'en V3.
CHALLENGE_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["prompt", "palette"],
    "properties": {
        **GRAPH_BUILD_CONTENT["properties"],
        "brief": {"type": "string"},
        "success_criteria": {"type": "array", "items": _TEXT},
    },
    "additionalProperties": False,
}

CHALLENGE_SOLUTION = GRAPH_REQUIREMENTS_SOLUTION


# ---------------------------------------------------------------------------
# H - Completer le graphe
# ---------------------------------------------------------------------------
GRAPH_COMPLETE_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["prompt", "partial_graph", "palette"],
    "properties": {
        "prompt": _TEXT,
        # Blueprint partiel : il manque des nodes et/ou des connexions.
        "partial_graph": NORMALIZED_GRAPH_SCHEMA,
        "palette": _PALETTE,
        "variables": {"type": "array", "items": VARIABLE_SCHEMA},
        # Nodes deja en place, non modifiables : c'est ce qui contraint
        # l'espace des solutions et limite les faux negatifs.
        "locked_node_ids": {"type": "array", "items": _ID},
        # Emplacements vides materialises sur le canvas.
        "slots": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id"],
                "properties": {
                    "id": _ID,
                    "label": {"type": "string"},
                    "position": {
                        "type": "object",
                        "required": ["x", "y"],
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

GRAPH_COMPLETE_SOLUTION = GRAPH_REQUIREMENTS_SOLUTION


# ---------------------------------------------------------------------------
# I - Realiser dans Unreal, puis coller le texte exporte
# ---------------------------------------------------------------------------
# Meme moteur de validation que les autres types de production : le texte colle
# est normalise en graphe avant comparaison. Jamais de parsing binaire .uasset.
UNREAL_EXPORT_CONTENT: dict[str, Any] = {
    "type": "object",
    "required": ["prompt", "instructions"],
    "properties": {
        "prompt": _TEXT,
        # Marche a suivre dans l'editeur Unreal, etape par etape.
        "instructions": {"type": "array", "minItems": 1, "items": _TEXT},
        "blueprint_context": {
            "type": "string",
            "description": "Ou realiser l'exercice : Level Blueprint, Actor BP...",
        },
        "unreal_version": {"type": "string"},
        "reference_image_url": {"type": "string"},
        # Rappel de la manipulation : selectionner les nodes, Ctrl+C, coller ici.
        "export_hint": {"type": "string"},
    },
    "additionalProperties": False,
}

UNREAL_EXPORT_SOLUTION = GRAPH_REQUIREMENTS_SOLUTION
