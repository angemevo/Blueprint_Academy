"""Catalogue de nodes Blueprint : le vocabulaire unique de la plateforme.

Decision verrouillee (CLAUDE.md > Catalogue de nodes) : ce module est LE
vocabulaire. Palettes, graphes fournis par un enonce et solutions designent
tous un node par son identifiant de catalogue.

## Forme des identifiants

Un identifiant doit etre DERIVABLE MECANIQUEMENT du copier-comme-texte de
l'editeur UE5, sans table de correspondance. Cet export donne, pour chaque
node, une classe et - quand le node en a un - un membre :

    Begin Object Class=/Script/BlueprintGraph.K2Node_Event Name="K2Node_Event_0"
       EventReference=(MemberParent=Class'"/Script/Engine.Actor"',
                       MemberName="ReceiveBeginPlay")

D'ou la regle, implementee par `derive_node_id()` :

    <classe courte>              quand le node n'a pas de membre  -> K2Node_IfThenElse
    <classe courte>:<MemberName> sinon                            -> K2Node_Event:ReceiveBeginPlay

C'est la raison pour laquelle on n'utilise PAS les noms affiches comme
identifiants : « Event BeginPlay » ne se derive pas de `ReceiveBeginPlay`,
« Branch » ne correspond a aucun membre, et « For Loop » est en realite une
instance de macro. Les noms affiches restent exacts, mais comme LIBELLES.

## Ce qui n'est pas dans l'identifiant

Les donnees propres a une instance - nom de la variable lue, classe ciblee par
un Cast, valeur litterale - ne font pas partie du type. Elles vivent dans
`node["properties"]` et se verifient avec le `match` d'un selecteur. Sans quoi
il faudrait un type de node par variable du projet.

## Politique de contenu

Le noyau est volontairement CONSERVATEUR : on n'y met que ce qui a ete verifie
dans l'editeur. CLAUDE.md est explicite - en cas de doute, Unreal a raison, et
mieux vaut ne rien enseigner qu'enseigner approximativement. Un node non encore
verifie s'ajoute par configuration (`BLUEPRINT_EXTRA_NODE_TYPES`), puis rejoint
le noyau une fois confirme sur un vrai projet.

Evolution prevue (CLAUDE.md) : le catalogue decrira aussi les PINS de chaque
node et sera servi par l'API au canvas.
"""

from dataclasses import dataclass

from django.conf import settings


class NodeCategory:
    """Categories de la palette, calquees sur celles de l'editeur."""

    EVENTS = "events"
    FLOW_CONTROL = "flow_control"
    VARIABLES = "variables"
    FUNCTIONS = "functions"
    MATH = "math"
    ACTORS = "actors"
    COMPONENTS = "components"
    UI = "ui"
    AUDIO_FX = "audio_fx"
    UTILITY = "utility"


@dataclass(frozen=True)
class NodeType:
    """Une entree du catalogue."""

    #: Identifiant derive de l'export UE5. Cle unique de tout le systeme.
    id: str
    #: Nom affiche, identique a celui de l'editeur UE5.
    label: str
    category: str
    #: Classe proprietaire du membre, telle qu'elle apparait dans MemberParent.
    #: Informatif : sert a lever une ambiguite et a documenter, pas a identifier.
    member_parent: str = ""


def derive_node_id(class_path: str, member_name: str | None = None) -> str:
    """Construit un identifiant a partir des tokens d'un export UE5.

    `class_path` est la valeur de `Class=` (chemin complet ou nom court),
    `member_name` celle de `MemberName=` quand le node en porte un.

    >>> derive_node_id("/Script/BlueprintGraph.K2Node_Event", "ReceiveBeginPlay")
    'K2Node_Event:ReceiveBeginPlay'
    >>> derive_node_id("/Script/BlueprintGraph.K2Node_IfThenElse")
    'K2Node_IfThenElse'
    """
    class_name = class_path.rsplit(".", 1)[-1].strip("'\" ")
    if member_name:
        return f"{class_name}:{member_name}"
    return class_name


def _node(
    class_path: str,
    member_name: str | None,
    label: str,
    category: str,
    member_parent: str = "",
) -> NodeType:
    return NodeType(
        id=derive_node_id(class_path, member_name),
        label=label,
        category=category,
        member_parent=member_parent,
    )


_ENGINE = "/Script/Engine"
_KISMET_SYSTEM = "/Script/Engine.KismetSystemLibrary"
_KISMET_MATH = "/Script/Engine.KismetMathLibrary"
_GAMEPLAY_STATICS = "/Script/Engine.GameplayStatics"
_ACTOR = "/Script/Engine.Actor"
_BPG = "/Script/BlueprintGraph"

# ---------------------------------------------------------------------------
# Noyau du catalogue
# ---------------------------------------------------------------------------
_CORE: tuple[NodeType, ...] = (
    # --- Evenements ---------------------------------------------------------
    _node(_BPG + ".K2Node_Event", "ReceiveBeginPlay", "Event BeginPlay", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveTick", "Event Tick", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveActorBeginOverlap", "Event ActorBeginOverlap", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveActorEndOverlap", "Event ActorEndOverlap", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveHit", "Event Hit", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveAnyDamage", "Event AnyDamage", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveEndPlay", "Event EndPlay", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveDestroyed", "Event Destroyed", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_CustomEvent", None, "Custom Event", NodeCategory.EVENTS),
    # --- Controle de flux ---------------------------------------------------
    _node(_BPG + ".K2Node_IfThenElse", None, "Branch", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_ExecutionSequence", None, "Sequence", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "ForLoop", "For Loop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "ForLoopWithBreak", "For Loop with Break", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "ForEachLoop", "For Each Loop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "WhileLoop", "While Loop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "DoOnce", "Do Once", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "DoN", "Do N", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "FlipFlop", "FlipFlop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "Gate", "Gate", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "MultiGate", "MultiGate", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "IsValid", "Is Valid", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchInteger", None, "Switch on Int", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchString", None, "Switch on String", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchEnum", None, "Switch on Enum", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_Select", None, "Select", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_CallFunction", "Delay", "Delay", NodeCategory.FLOW_CONTROL, _KISMET_SYSTEM),
    _node(_BPG + ".K2Node_CallFunction", "RetriggerableDelay", "Retriggerable Delay", NodeCategory.FLOW_CONTROL, _KISMET_SYSTEM),
    # --- Variables, structures, fonctions -----------------------------------
    # Le nom de la variable n'est PAS dans l'identifiant : il se cible avec
    # `match: {"variable": "..."}`.
    _node(_BPG + ".K2Node_VariableGet", None, "Get", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_VariableSet", None, "Set", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_MakeStruct", None, "Make Struct", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_BreakStruct", None, "Break Struct", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_DynamicCast", None, "Cast To", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_FunctionEntry", None, "Function Entry", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_FunctionResult", None, "Return Node", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_Timeline", None, "Timeline", NodeCategory.FUNCTIONS),
    # --- Mathematiques et logique -------------------------------------------
    # Seules les variantes entieres sont listees : les variantes flottantes ont
    # ete renommees pour le Large World Coordinates et demandent verification.
    _node(_BPG + ".K2Node_CallFunction", "Add_IntInt", "Add", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "Subtract_IntInt", "Subtract", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "Multiply_IntInt", "Multiply", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "Greater_IntInt", "Greater", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "Less_IntInt", "Less", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "EqualEqual_IntInt", "Equal", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "NotEqual_IntInt", "Not Equal", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "BooleanAND", "AND", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "BooleanOR", "OR", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "Not_PreBool", "NOT", NodeCategory.MATH, _KISMET_MATH),
    _node(_BPG + ".K2Node_CallFunction", "RandomIntegerInRange", "Random Integer in Range", NodeCategory.MATH, _KISMET_MATH),
    # --- Acteurs et gameplay -------------------------------------------------
    _node(_BPG + ".K2Node_SpawnActorFromClass", None, "Spawn Actor from Class", NodeCategory.ACTORS),
    _node(_BPG + ".K2Node_CallFunction", "K2_DestroyActor", "Destroy Actor", NodeCategory.ACTORS, _ACTOR),
    _node(_BPG + ".K2Node_CallFunction", "K2_GetActorLocation", "Get Actor Location", NodeCategory.ACTORS, _ACTOR),
    _node(_BPG + ".K2Node_CallFunction", "K2_SetActorLocation", "Set Actor Location", NodeCategory.ACTORS, _ACTOR),
    _node(_BPG + ".K2Node_CallFunction", "K2_GetActorRotation", "Get Actor Rotation", NodeCategory.ACTORS, _ACTOR),
    _node(_BPG + ".K2Node_CallFunction", "GetOwner", "Get Owner", NodeCategory.ACTORS, _ACTOR),
    _node(_BPG + ".K2Node_CallFunction", "GetPlayerCharacter", "Get Player Character", NodeCategory.ACTORS, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "GetPlayerController", "Get Player Controller", NodeCategory.ACTORS, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "GetAllActorsOfClass", "Get All Actors Of Class", NodeCategory.ACTORS, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "ApplyDamage", "Apply Damage", NodeCategory.ACTORS, _GAMEPLAY_STATICS),
    # --- Composants -----------------------------------------------------------
    _node(_BPG + ".K2Node_AddComponent", None, "Add Component", NodeCategory.COMPONENTS),
    # --- Interface, audio, effets, debogage -----------------------------------
    _node(_BPG + ".K2Node_CreateWidget", None, "Create Widget", NodeCategory.UI),
    _node(_BPG + ".K2Node_CallFunction", "AddToViewport", "Add to Viewport", NodeCategory.UI, _ENGINE + ".UserWidget"),
    _node(_BPG + ".K2Node_CallFunction", "RemoveFromParent", "Remove from Parent", NodeCategory.UI, _ENGINE + ".Widget"),
    _node(_BPG + ".K2Node_CallFunction", "PlaySound2D", "Play Sound 2D", NodeCategory.AUDIO_FX, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "PlaySoundAtLocation", "Play Sound at Location", NodeCategory.AUDIO_FX, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "PrintString", "Print String", NodeCategory.UTILITY, _KISMET_SYSTEM),
)

#: Noyau verifie, indexe par identifiant.
CORE_NODE_TYPES: dict[str, NodeType] = {node.id: node for node in _CORE}


def known_node_types() -> dict[str, NodeType]:
    """Catalogue effectif : le noyau, plus les ajouts de configuration.

    Un ajout par configuration n'a pas de libelle propre : son identifiant fait
    office de libelle jusqu'a son entree dans le noyau.
    """
    catalog = dict(CORE_NODE_TYPES)
    for node_id in getattr(settings, "BLUEPRINT_EXTRA_NODE_TYPES", ()):
        catalog.setdefault(
            node_id, NodeType(id=node_id, label=node_id, category=NodeCategory.UTILITY)
        )
    return catalog


def is_known_node_type(node_id: str) -> bool:
    return node_id in known_node_types()


def get_node_type(node_id: str) -> NodeType | None:
    return known_node_types().get(node_id)


def display_label(node_id: str) -> str:
    """Nom a afficher pour un identifiant, ou l'identifiant s'il est inconnu."""
    node = get_node_type(node_id)
    return node.label if node else node_id
