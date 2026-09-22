"""Tests du catalogue de nodes.

Le point critique n'est pas la taille du catalogue mais la FORME de ses
identifiants : ils doivent se deriver mecaniquement du copier-comme-texte
d'Unreal, sans table de correspondance (CLAUDE.md > Catalogue de nodes).
"""

from django.test import override_settings

from common.blueprint_catalog import (
    CORE_NODE_TYPES,
    NodeType,
    derive_node_id,
    display_label,
    get_node_type,
    is_known_node_type,
    known_node_types,
)

# Extraits representatifs d'un export UE5 : (Class=, MemberName=, identifiant).
# A remplacer par les valeurs d'un export reel des qu'il est disponible.
EXPORT_CASES = [
    ("/Script/BlueprintGraph.K2Node_Event", "ReceiveBeginPlay", "K2Node_Event:ReceiveBeginPlay"),
    ("/Script/BlueprintGraph.K2Node_Event", "ReceiveTick", "K2Node_Event:ReceiveTick"),
    ("/Script/BlueprintGraph.K2Node_CallFunction", "PrintString", "K2Node_CallFunction:PrintString"),
    ("/Script/BlueprintGraph.K2Node_IfThenElse", None, "K2Node_IfThenElse"),
    ("/Script/BlueprintGraph.K2Node_VariableGet", None, "K2Node_VariableGet"),
    ("/Script/BlueprintGraph.K2Node_MacroInstance", "ForLoop", "K2Node_MacroInstance:ForLoop"),
]


def test_identifiers_are_derived_from_the_export_tokens():
    for class_path, member_name, expected in EXPORT_CASES:
        assert derive_node_id(class_path, member_name) == expected


def test_derivation_accepts_a_quoted_class_path():
    """L'export ecrit parfois la classe entre quotes : Class'"/Script/...'."""
    assert derive_node_id('Class\'"/Script/Engine.Actor"\'') == "Actor"


def test_every_derived_identifier_is_in_the_catalog():
    """Tout ce que l'export produit dans ces cas doit etre reconnu."""
    for class_path, member_name, _ in EXPORT_CASES:
        node_id = derive_node_id(class_path, member_name)
        assert is_known_node_type(node_id), f"{node_id} absent du catalogue"


def test_catalog_ids_are_all_reconstructible():
    """Un identifiant du catalogue doit pouvoir sortir de `derive_node_id`.

    C'est le verrou de la regle : si une entree etait ecrite a la main sous une
    autre forme, le normaliseur du type I ne la retrouverait jamais.
    """
    for node_id in CORE_NODE_TYPES:
        class_name, _, member_name = node_id.partition(":")
        assert derive_node_id(class_name, member_name or None) == node_id
        assert class_name.startswith("K2Node_"), (
            f"{node_id} : un identifiant part toujours d'une classe de node"
        )


def test_display_labels_are_not_identifiers():
    """Les libelles sont ceux de l'editeur, les identifiants ceux de l'export."""
    assert display_label("K2Node_Event:ReceiveBeginPlay") == "Event BeginPlay"
    assert display_label("K2Node_IfThenElse") == "Branch"
    assert display_label("K2Node_MacroInstance:ForLoop") == "For Loop"


def test_labels_are_unique_enough_to_be_displayed():
    """Deux entrees peuvent partager un libelle, jamais un identifiant."""
    assert len(CORE_NODE_TYPES) == len({node.id for node in CORE_NODE_TYPES.values()})


def test_unknown_identifier_falls_back_to_itself():
    assert get_node_type("K2Node_Inconnu") is None
    assert display_label("K2Node_Inconnu") == "K2Node_Inconnu"


@override_settings(BLUEPRINT_EXTRA_NODE_TYPES=["K2Node_CallFunction:MaFonction"])
def test_catalog_can_be_extended_without_shipping_code():
    assert is_known_node_type("K2Node_CallFunction:MaFonction")
    assert isinstance(known_node_types()["K2Node_CallFunction:MaFonction"], NodeType)


@override_settings(BLUEPRINT_EXTRA_NODE_TYPES=["K2Node_CallFunction:PrintString"])
def test_configuration_never_overrides_a_verified_entry():
    """Le noyau verifie garde la main sur son libelle."""
    assert display_label("K2Node_CallFunction:PrintString") == "Print String"
