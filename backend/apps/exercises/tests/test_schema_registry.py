"""Tests du registre de schemas et des controles de coherence.

Aucun acces base : on teste la validation de contenu pure, celle qui protege du
risque numero 1 du projet (justesse du contenu Blueprint).
"""

from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError

from apps.exercises.enums import ExerciseType
from apps.exercises.schemas import EXERCISE_SCHEMAS, validate_exercise_payload
from common.schemas import error_sort_key

# --- Briques de payload valides, reutilisees par les cas d'erreur ------------

BEGIN_PLAY = "K2Node_Event:ReceiveBeginPlay"
PRINT_STRING = "K2Node_CallFunction:PrintString"
SET_VARIABLE = "K2Node_VariableSet"

PALETTE = [{"type": BEGIN_PLAY}, {"type": PRINT_STRING}]
REQUIREMENTS = {
    "required_nodes": [{"type": PRINT_STRING, "min_count": 1}],
    "required_edges": [
        {
            "from": {"type": BEGIN_PLAY},
            "to": {"type": PRINT_STRING},
            "from_pin": "then",
            "to_pin": "exec",
        }
    ],
}


def expect_errors(exercise_type, content, solution) -> dict[str, list[str]]:
    """Valide en attendant un echec, et rend les messages ranges par champ."""
    with pytest.raises(ValidationError) as caught:
        validate_exercise_payload(exercise_type, content, solution)
    return caught.value.message_dict


# --- Couverture du registre ---------------------------------------------------


def test_registry_covers_every_exercise_type():
    """Un type sans schema serait accepte sans aucun controle."""
    assert set(EXERCISE_SCHEMAS) == set(ExerciseType)


def test_declared_graph_keys_exist_in_content_schema():
    """`graph_keys` pilote l'integrite : une cle mal orthographiee ne verifierait rien."""
    for exercise_type, schema in EXERCISE_SCHEMAS.items():
        for key in schema.graph_keys:
            assert key in schema.content["properties"], (
                f"{exercise_type} declare le graphe '{key}', absent de son schema"
            )


# --- Exigence positive obligatoire en production ------------------------------


def test_production_solution_requires_a_positive_requirement():
    """Interdire des nodes ne suffit pas : un canvas vide y satisferait."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        {"forbidden_nodes": [{"type": "K2Node_Event:ReceiveTick"}]},
    )
    assert "solution" in errors


def test_an_empty_submission_can_never_satisfy_a_debugging_exercise():
    """Verrou structurel : aucun exercice F satisfait par un graphe vide ne peut exister.

    Un graphe vide satisfait toute clause `forbidden_*` et toute liste
    d'exigences vide. Le schema interdit donc les deux formes qui laisseraient
    passer une soumission vide. Le test de bout en bout - soumettre vraiment un
    graphe vide au validateur - arrive en Phase 2b avec `apps.validation`.
    """
    broken = {
        "prompt": "Repare",
        "broken_graph": {
            "nodes": [{"id": "n1", "type": BEGIN_PLAY}],
            "edges": [],
        },
    }
    # 1. Aucune exigence positive : refuse.
    assert "solution" in expect_errors(
        ExerciseType.DEBUGGING,
        broken,
        {"forbidden_edges": [
            {"from": {"type": BEGIN_PLAY}, "to": {"type": BEGIN_PLAY}}
        ]},
    )
    # 2. Exigence positive presente mais VIDE : refuse aussi.
    assert "solution" in expect_errors(
        ExerciseType.DEBUGGING, broken, {"required_nodes": []}
    )


# --- Integrite des graphes fournis --------------------------------------------


def test_duplicate_node_ids_are_rejected():
    errors = expect_errors(
        ExerciseType.GRAPH_COMPLETE,
        {
            "prompt": "Complete",
            "palette": PALETTE,
            "partial_graph": {
                "nodes": [
                    {"id": "n1", "type": BEGIN_PLAY},
                    {"id": "n1", "type": PRINT_STRING},
                ],
                "edges": [],
            },
        },
        REQUIREMENTS,
    )
    assert any("ids de nodes en double" in message for message in errors["content"])


def test_edge_pointing_to_a_missing_node_is_rejected():
    errors = expect_errors(
        ExerciseType.DEBUGGING,
        {
            "prompt": "Repare",
            "broken_graph": {
                "nodes": [{"id": "n1", "type": BEGIN_PLAY}],
                "edges": [{"from": "n1", "to": "fantome", "from_pin": "then"}],
            },
        },
        REQUIREMENTS,
    )
    assert any("nodes inexistants" in message for message in errors["content"])


def test_reference_graph_problems_are_filed_under_solution():
    """Le graphe de reference vit dans la solution : l'erreur aussi."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        {
            **REQUIREMENTS,
            "reference_graph": {
                "nodes": [{"id": "n1", "type": BEGIN_PLAY}],
                "edges": [{"from": "n1", "to": "absent"}],
            },
        },
    )
    assert "solution" in errors
    assert "content" not in errors


# --- Pins : from_pin / to_pin, plus de champ `pin` ----------------------------


def test_edge_with_a_single_pin_field_is_rejected():
    """Une connexion relie deux pins nommes : `pin` seul ne veut rien dire."""
    errors = expect_errors(
        ExerciseType.DEBUGGING,
        {
            "prompt": "Repare",
            "broken_graph": {
                "nodes": [
                    {"id": "n1", "type": BEGIN_PLAY},
                    {"id": "n2", "type": PRINT_STRING},
                ],
                "edges": [{"from": "n1", "to": "n2", "pin": "exec"}],
            },
        },
        REQUIREMENTS,
    )
    assert "content" in errors


def test_edge_selector_accepts_from_pin_and_to_pin():
    validate_exercise_payload(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        REQUIREMENTS,
    )


# --- Unicite des identifiants et appariement ----------------------------------


def test_duplicate_option_ids_are_rejected():
    errors = expect_errors(
        ExerciseType.MCQ,
        {
            "question": "Lequel ?",
            "options": [
                {"id": "o1", "text": "Event BeginPlay"},
                {"id": "o1", "text": "Event Tick"},
            ],
        },
        {"correct_option_ids": ["o1"]},
    )
    assert any("ids en double" in message for message in errors["content"])


def test_duplicate_item_ids_are_rejected():
    errors = expect_errors(
        ExerciseType.ORDERING,
        {
            "items": [
                {"id": "i1", "label": "Event BeginPlay"},
                {"id": "i1", "label": "Print String"},
            ]
        },
        {"order": ["i1"]},
    )
    assert any("ids en double" in message for message in errors["content"])


def test_matching_rejects_a_left_item_paired_twice():
    errors = expect_errors(
        ExerciseType.NODE_MATCHING,
        {
            "left": [{"id": "l1", "label": "Event Tick"}, {"id": "l2", "label": "Delay"}],
            "right": [
                {"id": "r1", "label": "Chaque frame"},
                {"id": "r2", "label": "Attend"},
            ],
        },
        {
            "pairs": [
                {"left_id": "l1", "right_id": "r1"},
                {"left_id": "l1", "right_id": "r2"},
            ]
        },
    )
    messages = " ".join(errors["solution"])
    assert "une seule cible" in messages
    assert "sans association" in messages  # l2 n'est apparie nulle part


# --- Selecteurs : type, match, faisabilite ------------------------------------


def test_required_node_absent_from_palette_is_rejected():
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": [PALETTE[0]]},
        {"required_nodes": [{"type": "K2Node_SpawnActorFromClass"}]},
    )
    assert any("insoluble" in message for message in errors["solution"])


def test_edge_selector_sides_are_checked_against_the_palette():
    """Les deux bouts d'une connexion sont des selecteurs, controles comme tels."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": [PALETTE[0]]},
        {
            "required_edges": [
                {"from": {"type": BEGIN_PLAY}, "to": {"type": PRINT_STRING}}
            ]
        },
    )
    assert any("required_edges.to" in message for message in errors["solution"])


def test_selector_match_on_an_undeclared_variable_is_rejected():
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Incremente le score",
            "palette": [*PALETTE, {"type": SET_VARIABLE}],
        },
        {"required_nodes": [{"type": SET_VARIABLE, "match": {"variable": "Score"}}]},
    )
    assert any("variable 'Score'" in message for message in errors["solution"])


def test_selector_match_on_a_declared_variable_is_accepted():
    validate_exercise_payload(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Incremente le score",
            "palette": [*PALETTE, {"type": SET_VARIABLE}],
            "variables": [{"name": "Score", "type": "integer"}],
        },
        {
            "required_nodes": [{"type": SET_VARIABLE, "match": {"variable": "Score"}}],
            "required_edges": [
                {
                    "from": {"type": BEGIN_PLAY},
                    "to": {"type": SET_VARIABLE, "match": {"variable": "Score"}},
                    "from_pin": "then",
                }
            ],
        },
    )


def test_selector_on_an_author_named_class_requires_a_match():
    """« Il faut un Set » ne valide rien : il faut dire lequel."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Mets le score a jour",
            "palette": [*PALETTE, {"type": SET_VARIABLE}],
            "variables": [{"name": "Score", "type": "integer"}],
        },
        {"required_nodes": [{"type": SET_VARIABLE}]},
    )
    assert any("match.variable" in message for message in errors["solution"])


def test_selector_on_a_blueprint_function_requires_its_name():
    """Un appel de fonction du Blueprint sans nom vise n'importe quel appel."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Appelle ta fonction",
            "palette": [*PALETTE, {"type": "K2Node_CallFunction"}],
        },
        {"required_nodes": [{"type": "K2Node_CallFunction"}]},
    )
    assert any("match.function" in message for message in errors["solution"])


def test_an_engine_function_needs_no_match():
    """Le nom du moteur est deja dans l'identifiant : rien a preciser."""
    validate_exercise_payload(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Affiche un message", "palette": PALETTE},
        {"required_nodes": [{"type": PRINT_STRING}]},
    )


def test_unknown_match_key_is_rejected():
    """Le vocabulaire de `match` est ferme : une cle inventee ne filtrerait rien."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        {"required_nodes": [{"type": PRINT_STRING, "match": {"varaible": "Score"}}]},
    )
    assert "solution" in errors


def test_required_variable_must_be_declared_in_content():
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        {"required_variables": [{"name": "Health", "type": "float"}]},
    )
    assert any("Health" in message for message in errors["solution"])


def test_required_variable_type_must_match_the_declared_one():
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Construis",
            "palette": PALETTE,
            "variables": [{"name": "Health", "type": "integer"}],
        },
        {"required_variables": [{"name": "Health", "type": "float"}]},
    )
    assert any("exigee en 'float'" in message for message in errors["solution"])


# --- Catalogue : le vocabulaire unique de la plateforme -----------------------


def test_unreal_export_rejects_a_node_absent_from_the_catalog():
    """Sans palette, le catalogue est le seul garde-fou du type I."""
    errors = expect_errors(
        ExerciseType.UNREAL_EXPORT,
        {"prompt": "Reproduis", "instructions": ["Ouvre le Level Blueprint"]},
        {"required_nodes": [{"type": "Evenement Demarrage"}]},
    )
    assert any("absents du catalogue" in message for message in errors["solution"])


def test_palette_rejects_a_node_absent_from_the_catalog():
    """Le catalogue s'applique aux palettes, pas seulement aux solutions."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": [{"type": "Affiche Un Message"}]},
        {"required_nodes": [{"type": PRINT_STRING}]},
    )
    assert any("palette" in message for message in errors["content"])


def test_palette_label_must_match_the_editor_name():
    """Fidelite a Unreal : un enonce ne renomme pas un node."""
    errors = expect_errors(
        ExerciseType.GRAPH_BUILD,
        {
            "prompt": "Construis",
            "palette": [{"type": PRINT_STRING, "label": "Afficher un texte"}],
        },
        {"required_nodes": [{"type": PRINT_STRING}]},
    )
    assert any("nom affiche par l'editeur" in message for message in errors["content"])


def test_palette_label_may_be_omitted():
    """Le libelle vient du catalogue : l'enonce n'a pas a le repeter."""
    validate_exercise_payload(
        ExerciseType.GRAPH_BUILD,
        {"prompt": "Construis", "palette": PALETTE},
        REQUIREMENTS,
    )


def test_provided_graph_rejects_a_node_absent_from_the_catalog():
    errors = expect_errors(
        ExerciseType.DEBUGGING,
        {
            "prompt": "Repare",
            "broken_graph": {
                "nodes": [{"id": "n1", "type": "Node Invente"}],
                "edges": [],
            },
        },
        REQUIREMENTS,
    )
    assert any("broken_graph" in message for message in errors["content"])


def test_illustration_graph_of_a_recall_type_is_checked_too():
    """Un QCM qui illustre un node inexistant enseigne une erreur."""
    errors = expect_errors(
        ExerciseType.MCQ,
        {
            "question": "Que fait ce graphe ?",
            "options": [
                {"id": "o1", "text": "Rien"},
                {"id": "o2", "text": "Affiche un message"},
            ],
            "graph": {"nodes": [{"id": "n1", "type": "Imprimer Texte"}], "edges": []},
        },
        {"correct_option_ids": ["o2"]},
    )
    assert any("absents du catalogue" in message for message in errors["content"])


def test_unreal_export_checks_forbidden_clauses_too():
    """Une faute de frappe dans un `forbidden_*` rend la clause inoperante."""
    errors = expect_errors(
        ExerciseType.UNREAL_EXPORT,
        {"prompt": "Reproduis", "instructions": ["Ouvre le Level Blueprint"]},
        {**REQUIREMENTS, "forbidden_nodes": [{"type": "Evnt Tick"}]},
    )
    assert any("Evnt Tick" in message for message in errors["solution"])


def test_unreal_export_accepts_catalog_node_types():
    validate_exercise_payload(
        ExerciseType.UNREAL_EXPORT,
        {"prompt": "Reproduis", "instructions": ["Ouvre le Level Blueprint"]},
        REQUIREMENTS,
    )


# --- Type A : plus d'indice dans le contenu ------------------------------------


def test_question_content_no_longer_accepts_a_hint():
    """Les indices progressifs vivent sur `Exercise.hints`, pour tous les types."""
    errors = expect_errors(
        ExerciseType.QUESTION,
        {"question": "Quel node demarre le jeu ?", "hint": "Il commence par Event"},
        {"accepted_answers": ["Event BeginPlay"]},
    )
    assert "content" in errors


# --- Routage des messages ------------------------------------------------------


def test_content_and_solution_errors_are_reported_separately():
    errors = expect_errors(
        ExerciseType.MCQ,
        {
            "question": "Lequel ?",
            "options": [
                {"id": "o1", "text": "Event BeginPlay"},
                {"id": "o1", "text": "Event Tick"},
            ],
        },
        {"correct_option_ids": ["inconnu"]},
    )
    assert set(errors) == {"content", "solution"}
    assert any("ids en double" in message for message in errors["content"])
    assert any("inexistantes" in message for message in errors["solution"])


def test_error_sort_key_handles_paths_mixing_keys_and_indexes():
    """Trier sur les segments bruts leverait TypeError : int vs str."""
    paths = [
        SimpleNamespace(path=["blocks", 2, "text"]),
        SimpleNamespace(path=["blocks", "extra"]),
        SimpleNamespace(path=[]),
    ]
    assert [error_sort_key(error) for error in sorted(paths, key=error_sort_key)] == [
        [],
        ["blocks", "2", "text"],
        ["blocks", "extra"],
    ]
