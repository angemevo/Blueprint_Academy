"""Tests du catalogue de nodes, adosses a un export UE5 reel.

Le point critique n'est pas la taille du catalogue mais la FORME de ses
identifiants : ils doivent se deriver mecaniquement du copier-comme-texte
d'Unreal, sans table de correspondance (CLAUDE.md > Catalogue de nodes).

`fixtures/export_ue5.txt` est un export reel (UE 5.7.4) d'un Blueprint de test.
C'est la seule source de verite de ces tests : rien n'y est reconstitue.
"""

import re
from pathlib import Path

from django.test import override_settings

from common.blueprint_catalog import (
    CORE_NODE_TYPES,
    DUAL_CLASSES,
    USER_NAMED_CLASSES,
    NodeType,
    derive_node_id,
    display_label,
    expected_match_key,
    get_node_type,
    is_known_node_type,
    known_node_types,
    split_node_id,
)

EXPORT_PATH = Path(__file__).parent / "fixtures" / "export_ue5.txt"


# ---------------------------------------------------------------------------
# Lecture de l'export
# ---------------------------------------------------------------------------
# Extraction volontairement minimale : on ne lit que l'IDENTITE de chaque node.
# Le normaliseur complet (pins, connexions, proprietes) arrive en Phase 2b dans
# `apps.validation` ; ces regex n'ont pas vocation a le prefigurer.

_BLOCK_RE = re.compile(r"^Begin Object Class=(\S+)", re.M)
_OPERATION_RE = re.compile(r'^\s*OperationName="([^"]+)"', re.M)
_ENGINE_MACRO_RE = re.compile(r'MacroGraph="[^"]*/Engine/[^"]*:([A-Za-z0-9_]+)\'"')
# Un membre du MOTEUR porte un MemberParent ; un membre du Blueprint n'en a pas
# (il a bSelfContext=True et un MemberGuid). C'est ce test qui decide s'il y a
# un discriminant.
_ENGINE_MEMBER_RE = re.compile(
    r'(?:Event|Function)Reference=\(MemberParent="[^"]+",MemberName="([^"]+)"'
)


def _discriminant(block: str) -> str | None:
    """Token identifiant d'un node, ou None s'il est nomme par l'auteur."""
    if match := _OPERATION_RE.search(block):
        # Prioritaire : un operateur promu porte AUSSI une FunctionReference,
        # mais celle-ci depend du type des fils branches.
        return match.group(1)
    if match := _ENGINE_MACRO_RE.search(block):
        return match.group(1)
    if match := _ENGINE_MEMBER_RE.search(block):
        return match.group(1)
    return None


def _exported_node_ids() -> list[str]:
    text = EXPORT_PATH.read_text(encoding="utf-8", errors="replace")
    blocks = _BLOCK_RE.split(text)[1:]
    # split() rend [classe, corps, classe, corps, ...]
    pairs = zip(blocks[::2], blocks[1::2], strict=True)
    return [
        derive_node_id(class_path, _discriminant(body)) for class_path, body in pairs
    ]


# ---------------------------------------------------------------------------
# Derivation depuis l'export reel
# ---------------------------------------------------------------------------
def test_export_fixture_is_a_real_ue5_export():
    header = EXPORT_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    assert header.startswith("Unreal Engine 5")


def test_every_exported_node_derives_to_a_known_identifier():
    """Le catalogue doit reconnaitre tout ce qu'un vrai export produit."""
    unknown = sorted({nid for nid in _exported_node_ids() if not is_known_node_type(nid)})
    assert not unknown, f"absents du catalogue : {unknown}"


def test_exported_identifiers_match_the_expected_set():
    assert set(_exported_node_ids()) == {
        "K2Node_Event:ReceiveBeginPlay",
        "K2Node_IfThenElse",
        "K2Node_VariableGet",
        "K2Node_VariableSet",
        "K2Node_PromotableOperator:Add",
        "K2Node_CallFunction:PrintString",
        "K2Node_CallFunction:Conv_DoubleToString",
        "K2Node_MacroInstance:ForLoop",
        "K2Node_CustomEvent",
        # Fonction definie dans le Blueprint (bSelfContext, pas de MemberParent) :
        # son nom « ApplyDamage » n'entre pas dans l'identifiant.
        "K2Node_CallFunction",
    }


def test_a_promoted_operator_is_identified_by_its_operation():
    """Sinon l'identifiant dependrait du type des fils branches.

    L'export contient un « + » resolu en `Add_DoubleDouble`. Retenir ce nom
    ferait echouer l'exercice pour un eleve qui branche des entiers - un faux
    negatif, precisement ce que CLAUDE.md interdit.
    """
    text = EXPORT_PATH.read_text(encoding="utf-8", errors="replace")
    assert "Add_DoubleDouble" in text
    assert "K2Node_PromotableOperator:Add" in _exported_node_ids()
    assert not any(nid.endswith("Add_DoubleDouble") for nid in _exported_node_ids())


def test_author_named_elements_never_reach_the_identifier():
    """Variable, evenement personnalise et fonction du Blueprint : classe seule."""
    text = EXPORT_PATH.read_text(encoding="utf-8", errors="replace")
    # Ces noms existent bien dans l'export...
    for author_name in ("Health", "bIsAlive", "OnDamaged", "ApplyDamage"):
        assert author_name in text
    # ... mais aucun ne doit apparaitre dans un identifiant derive.
    derived = " ".join(_exported_node_ids())
    for author_name in ("Health", "bIsAlive", "OnDamaged"):
        assert author_name not in derived


# ---------------------------------------------------------------------------
# Forme des identifiants du catalogue
# ---------------------------------------------------------------------------
def test_catalog_ids_are_all_reconstructible():
    """Une entree ecrite sous une autre forme serait introuvable a la validation."""
    for node_id in CORE_NODE_TYPES:
        class_name, discriminant = split_node_id(node_id)
        assert derive_node_id(class_name, discriminant or None) == node_id
        assert class_name.startswith("K2Node_"), (
            f"{node_id} : un identifiant part toujours d'une classe de node"
        )


def test_author_named_classes_carry_no_discriminant():
    for node_id in CORE_NODE_TYPES:
        class_name, discriminant = split_node_id(node_id)
        if class_name in USER_NAMED_CLASSES:
            assert not discriminant, f"{node_id} : nom d'auteur dans l'identifiant"


def test_dual_classes_exist_in_both_forms():
    """Appel de fonction et macro existent en version moteur ET en version auteur."""
    for class_name in DUAL_CLASSES:
        assert is_known_node_type(class_name), f"{class_name} seul manque au catalogue"
        assert any(
            split_node_id(node_id) == (class_name, discriminant)
            for node_id in CORE_NODE_TYPES
            for discriminant in [split_node_id(node_id)[1]]
            if discriminant
        ), f"aucune variante moteur pour {class_name}"


def test_expected_match_key_targets_the_right_selectors():
    assert expected_match_key("K2Node_VariableSet") == "variable"
    assert expected_match_key("K2Node_CustomEvent") == "event"
    assert expected_match_key("K2Node_CallFunction") == "function"
    assert expected_match_key("K2Node_MacroInstance") == "macro"
    # Une variante moteur est deja sans ambiguite.
    assert expected_match_key("K2Node_CallFunction:PrintString") is None
    assert expected_match_key("K2Node_IfThenElse") is None


def test_derivation_accepts_the_quoted_class_path_of_the_export():
    """L'export ecrit les classes parentes sous forme citee."""
    assert derive_node_id("/Script/CoreUObject.Class'/Script/Engine.Actor'") == "Actor"


# ---------------------------------------------------------------------------
# Libelles et extension
# ---------------------------------------------------------------------------
def test_display_labels_are_not_identifiers():
    assert display_label("K2Node_Event:ReceiveBeginPlay") == "Event BeginPlay"
    assert display_label("K2Node_IfThenElse") == "Branch"
    assert display_label("K2Node_MacroInstance:ForLoop") == "For Loop"


def test_verified_entries_are_the_ones_seen_in_the_export():
    """`verified` veut dire « observe », pas « probable »."""
    verified = {node.id for node in CORE_NODE_TYPES.values() if node.verified}
    assert verified == set(_exported_node_ids())


def test_unknown_identifier_falls_back_to_itself():
    assert get_node_type("K2Node_Inconnu") is None
    assert display_label("K2Node_Inconnu") == "K2Node_Inconnu"


@override_settings(BLUEPRINT_EXTRA_NODE_TYPES=["K2Node_CallFunction:MaFonction"])
def test_catalog_can_be_extended_without_shipping_code():
    assert is_known_node_type("K2Node_CallFunction:MaFonction")
    assert isinstance(known_node_types()["K2Node_CallFunction:MaFonction"], NodeType)


@override_settings(BLUEPRINT_EXTRA_NODE_TYPES=["K2Node_CallFunction:PrintString"])
def test_configuration_never_overrides_a_verified_entry():
    assert display_label("K2Node_CallFunction:PrintString") == "Print String"
