"""Catalogue de nodes Blueprint : le vocabulaire unique de la plateforme.

Decision verrouillee (CLAUDE.md > Catalogue de nodes) : ce module est LE
vocabulaire. Palettes, graphes fournis par un enonce et solutions designent
tous un node par son identifiant de catalogue.

## Forme des identifiants

Un identifiant se derive MECANIQUEMENT du copier-comme-texte de l'editeur UE5 :

    <classe courte>[:<discriminant>]

La classe vient du `Class=` de l'export. Le discriminant n'apparait QUE lorsque
le node designe un element du MOTEUR, dont le nom fait partie du vocabulaire
d'Unreal et ne changera pas d'un projet a l'autre :

| Classe                     | Discriminant                    | Exemple                             |
|----------------------------|---------------------------------|-------------------------------------|
| K2Node_Event               | EventReference.MemberName       | K2Node_Event:ReceiveBeginPlay       |
| K2Node_CallFunction        | FunctionReference.MemberName    | K2Node_CallFunction:PrintString     |
|   (si MemberParent moteur) |                                 |                                     |
| K2Node_MacroInstance       | nom du graphe de macro          | K2Node_MacroInstance:ForLoop        |
|   (si macro sous /Engine/) |                                 |                                     |
| K2Node_PromotableOperator  | OperationName                   | K2Node_PromotableOperator:Add       |

## Elements nommes par l'auteur : jamais dans l'identifiant

Une variable, un evenement personnalise, une fonction ou une macro creee dans
le Blueprint portent un nom CHOISI. Les mettre dans l'identifiant creerait un
type de node par variable de chaque projet. Leur identifiant est donc la classe
seule, et le nom propre se verifie par un selecteur `match` :

    {"type": "K2Node_VariableSet", "match": {"variable": "Health"}}
    {"type": "K2Node_CustomEvent", "match": {"event": "OnDamaged"}}
    {"type": "K2Node_CallFunction", "match": {"function": "ApplyDamage"}}
    {"type": "K2Node_MacroInstance", "match": {"macro": "MaMacro"}}

L'export distingue les deux cas sans ambiguite : un membre du moteur porte un
`MemberParent="/Script/..."`, un membre du Blueprint porte `bSelfContext=True`
et un `MemberGuid`. C'est ce test, et lui seul, qui decide de la presence d'un
discriminant.

## Le cas des operateurs promus

Depuis UE5, poser un « + » depuis la palette cree un `K2Node_PromotableOperator`
dont la fonction resolue depend du type des fils branches (`Add_DoubleDouble`,
`Add_IntInt`...). Identifier ce node par sa fonction resolue produirait des faux
negatifs : le meme exercice echouerait selon que l'eleve branche un entier ou un
flottant. On retient donc `OperationName`, stable et independant des types.

## Politique de contenu

`verified=True` signifie « observe dans un export reel ». Le reste vient de la
documentation et attend confirmation dans l'editeur : CLAUDE.md est explicite,
en cas de doute Unreal a raison. Un node manquant s'ajoute sans livrer de code
via `BLUEPRINT_EXTRA_NODE_TYPES`, puis rejoint le noyau une fois confirme.

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


#: Classes dont le nom propre est toujours choisi par l'auteur du Blueprint :
#: leur identifiant ne porte JAMAIS de discriminant.
USER_NAMED_CLASSES = frozenset(
    {
        "K2Node_VariableGet",
        "K2Node_VariableSet",
        "K2Node_CustomEvent",
        "K2Node_FunctionEntry",
        "K2Node_FunctionResult",
    }
)

#: Classes qui designent tantot un element du moteur (avec discriminant),
#: tantot un element du Blueprint (sans). Cle `match` attendue dans le second cas.
DUAL_CLASSES = {
    "K2Node_CallFunction": "function",
    "K2Node_MacroInstance": "macro",
}

#: Cle `match` attendue quand un selecteur vise une classe sans discriminant.
MATCH_KEY_BY_CLASS = {
    "K2Node_VariableGet": "variable",
    "K2Node_VariableSet": "variable",
    "K2Node_CustomEvent": "event",
    **DUAL_CLASSES,
}


@dataclass(frozen=True)
class NodeType:
    """Une entree du catalogue."""

    #: Identifiant derive de l'export UE5. Cle unique de tout le systeme.
    id: str
    #: Nom affiche, identique a celui de l'editeur UE5.
    label: str
    category: str
    #: Classe proprietaire du membre, telle qu'elle apparait dans MemberParent.
    #: Informatif : leve une ambiguite et documente, n'identifie pas.
    member_parent: str = ""
    #: Observe dans un export reel, par opposition a « lu dans la doc ».
    verified: bool = False


def derive_node_id(class_path: str, discriminant: str | None = None) -> str:
    """Construit un identifiant a partir des tokens d'un export UE5.

    `class_path` est la valeur de `Class=` (chemin complet ou nom court).
    `discriminant` n'est fourni que pour un element du moteur : MemberName,
    nom de macro standard ou OperationName selon la classe. Pour un element
    nomme par l'auteur, il vaut None et le nom part dans les proprietes.

    >>> derive_node_id("/Script/BlueprintGraph.K2Node_Event", "ReceiveBeginPlay")
    'K2Node_Event:ReceiveBeginPlay'
    >>> derive_node_id("/Script/BlueprintGraph.K2Node_VariableSet")
    'K2Node_VariableSet'
    """
    class_name = class_path.rsplit(".", 1)[-1].strip("'\" ")
    if discriminant:
        return f"{class_name}:{discriminant}"
    return class_name


def split_node_id(node_id: str) -> tuple[str, str]:
    """Separe un identifiant en (classe, discriminant)."""
    class_name, _, discriminant = node_id.partition(":")
    return class_name, discriminant


def expected_match_key(node_id: str) -> str | None:
    """Cle `match` sans laquelle un selecteur sur ce node reste ambigu."""
    class_name, discriminant = split_node_id(node_id)
    if discriminant:
        return None
    return MATCH_KEY_BY_CLASS.get(class_name)


def _node(
    class_path: str,
    discriminant: str | None,
    label: str,
    category: str,
    member_parent: str = "",
    verified: bool = False,
) -> NodeType:
    return NodeType(
        id=derive_node_id(class_path, discriminant),
        label=label,
        category=category,
        member_parent=member_parent,
        verified=verified,
    )


_KISMET_SYSTEM = "/Script/Engine.KismetSystemLibrary"
_KISMET_MATH = "/Script/Engine.KismetMathLibrary"
_KISMET_STRING = "/Script/Engine.KismetStringLibrary"
_GAMEPLAY_STATICS = "/Script/Engine.GameplayStatics"
_ACTOR = "/Script/Engine.Actor"
_BPG = "/Script/BlueprintGraph"

# ---------------------------------------------------------------------------
# Noyau du catalogue
# ---------------------------------------------------------------------------
_CORE: tuple[NodeType, ...] = (
    # --- Evenements ---------------------------------------------------------
    _node(_BPG + ".K2Node_Event", "ReceiveBeginPlay", "Event BeginPlay", NodeCategory.EVENTS, _ACTOR, verified=True),
    _node(_BPG + ".K2Node_Event", "ReceiveTick", "Event Tick", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveActorBeginOverlap", "Event ActorBeginOverlap", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveActorEndOverlap", "Event ActorEndOverlap", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveHit", "Event Hit", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveAnyDamage", "Event AnyDamage", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveEndPlay", "Event EndPlay", NodeCategory.EVENTS, _ACTOR),
    _node(_BPG + ".K2Node_Event", "ReceiveDestroyed", "Event Destroyed", NodeCategory.EVENTS, _ACTOR),
    # Nom de l'evenement choisi par l'auteur -> match: {"event": "..."}.
    _node(_BPG + ".K2Node_CustomEvent", None, "Custom Event", NodeCategory.EVENTS, verified=True),
    # --- Controle de flux ---------------------------------------------------
    _node(_BPG + ".K2Node_IfThenElse", None, "Branch", NodeCategory.FLOW_CONTROL, verified=True),
    _node(_BPG + ".K2Node_ExecutionSequence", None, "Sequence", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "ForLoop", "For Loop", NodeCategory.FLOW_CONTROL, verified=True),
    _node(_BPG + ".K2Node_MacroInstance", "ForLoopWithBreak", "For Loop with Break", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "ForEachLoop", "For Each Loop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "WhileLoop", "While Loop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "DoOnce", "Do Once", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "DoN", "Do N", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "FlipFlop", "FlipFlop", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "Gate", "Gate", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "MultiGate", "MultiGate", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_MacroInstance", "IsValid", "Is Valid", NodeCategory.FLOW_CONTROL),
    # Macro definie dans le Blueprint -> match: {"macro": "..."}.
    _node(_BPG + ".K2Node_MacroInstance", None, "Macro", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchInteger", None, "Switch on Int", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchString", None, "Switch on String", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_SwitchEnum", None, "Switch on Enum", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_Select", None, "Select", NodeCategory.FLOW_CONTROL),
    _node(_BPG + ".K2Node_CallFunction", "Delay", "Delay", NodeCategory.FLOW_CONTROL, _KISMET_SYSTEM),
    _node(_BPG + ".K2Node_CallFunction", "RetriggerableDelay", "Retriggerable Delay", NodeCategory.FLOW_CONTROL, _KISMET_SYSTEM),
    # --- Variables, structures, fonctions -----------------------------------
    # Nom de la variable choisi par l'auteur -> match: {"variable": "..."}.
    _node(_BPG + ".K2Node_VariableGet", None, "Get", NodeCategory.VARIABLES, verified=True),
    _node(_BPG + ".K2Node_VariableSet", None, "Set", NodeCategory.VARIABLES, verified=True),
    _node(_BPG + ".K2Node_MakeStruct", None, "Make Struct", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_BreakStruct", None, "Break Struct", NodeCategory.VARIABLES),
    _node(_BPG + ".K2Node_DynamicCast", None, "Cast To", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_FunctionEntry", None, "Function Entry", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_FunctionResult", None, "Return Node", NodeCategory.FUNCTIONS),
    _node(_BPG + ".K2Node_Timeline", None, "Timeline", NodeCategory.FUNCTIONS),
    # Fonction definie dans le Blueprint -> match: {"function": "..."}.
    _node(_BPG + ".K2Node_CallFunction", None, "Call Function", NodeCategory.FUNCTIONS, verified=True),
    # --- Mathematiques et logique -------------------------------------------
    # Operateurs promus : identifies par OperationName, jamais par la fonction
    # resolue, qui depend du type des fils branches.
    _node(_BPG + ".K2Node_PromotableOperator", "Add", "Add", NodeCategory.MATH, verified=True),
    _node(_BPG + ".K2Node_PromotableOperator", "Subtract", "Subtract", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "Multiply", "Multiply", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "Divide", "Divide", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "Greater", "Greater", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "Less", "Less", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "Equal", "Equal", NodeCategory.MATH),
    _node(_BPG + ".K2Node_PromotableOperator", "NotEqual", "Not Equal", NodeCategory.MATH),
    _node(_BPG + ".K2Node_CallFunction", "RandomIntegerInRange", "Random Integer in Range", NodeCategory.MATH, _KISMET_MATH),
    # --- Conversions ---------------------------------------------------------
    _node(_BPG + ".K2Node_CallFunction", "Conv_DoubleToString", "To String", NodeCategory.UTILITY, _KISMET_STRING, verified=True),
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
    _node(_BPG + ".K2Node_CallFunction", "AddToViewport", "Add to Viewport", NodeCategory.UI, "/Script/UMG.UserWidget"),
    _node(_BPG + ".K2Node_CallFunction", "RemoveFromParent", "Remove from Parent", NodeCategory.UI, "/Script/UMG.Widget"),
    _node(_BPG + ".K2Node_CallFunction", "PlaySound2D", "Play Sound 2D", NodeCategory.AUDIO_FX, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "PlaySoundAtLocation", "Play Sound at Location", NodeCategory.AUDIO_FX, _GAMEPLAY_STATICS),
    _node(_BPG + ".K2Node_CallFunction", "PrintString", "Print String", NodeCategory.UTILITY, _KISMET_SYSTEM, verified=True),
)

#: Noyau du catalogue, indexe par identifiant.
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
