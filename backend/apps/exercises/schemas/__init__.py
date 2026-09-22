"""Registre des schemas JSON, un par type d'exercice (A-I).

Quatre niveaux de controle, appliques a la sauvegarde de chaque `Exercise` :

1. le SCHEMA JSON : la forme de `content` et de `solution` ;
2. l'INTEGRITE des graphes fournis par l'enonce : ids de nodes uniques, edges
   qui pointent vers des nodes existants ;
3. le VOCABULAIRE : tout node designe - palette, graphe fourni, selecteur -
   existe dans `common.blueprint_catalog`, le catalogue unique de la
   plateforme ;
4. la COHERENCE : les references croisees que JSON Schema ne sait pas exprimer
   (une bonne reponse qui designe une option inexistante, un node requis absent
   de la palette, une variable exigee mais jamais declaree...).

C'est ici que se rattrapent les erreurs d'auteur, premier risque du projet
selon CLAUDE.md. Chaque message est range sous le champ fautif (`content` ou
`solution`) pour s'afficher au bon endroit dans l'admin et dans l'API.
"""

from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from typing import Any

from django.core.exceptions import ValidationError

from common.blueprint_catalog import get_node_type, is_known_node_type
from common.schemas import validate_against_schema

from ..enums import GRAPH_BASED_TYPES, ExerciseType
from . import graph, interactive

Payload = dict[str, Any]
FieldErrors = dict[str, list[str]]

CONTENT = "content"
SOLUTION = "solution"


class ErrorCollector:
    """Accumule les messages de coherence en les rangeant par champ."""

    __slots__ = ("_by_field",)

    def __init__(self) -> None:
        self._by_field: FieldErrors = {}

    def add(self, field: str, message: str) -> None:
        self._by_field.setdefault(field, []).append(message)

    def as_dict(self) -> FieldErrors:
        return self._by_field

    def __bool__(self) -> bool:
        return bool(self._by_field)


#: Un controle de coherence lit l'enonce et la solution, et signale ce qui cloche.
CoherenceCheck = Callable[[Payload, Payload, ErrorCollector], None]


@dataclass(frozen=True)
class ExerciseSchema:
    """Contrat complet d'un type d'exercice."""

    content: dict[str, Any]
    solution: dict[str, Any]
    #: Cles de `content` qui portent un graphe fourni par l'enonce. Elles
    #: pilotent a la fois le controle d'integrite et celui de faisabilite.
    graph_keys: tuple[str, ...] = dataclass_field(default=())
    coherence: CoherenceCheck | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _dicts(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict)]


def _ids(items: Any, key: str = "id") -> set[str]:
    return {item[key] for item in _dicts(items) if key in item}


def _duplicates(values: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    duplicated: set[Any] = set()
    for value in values:
        if value in seen:
            duplicated.add(value)
        seen.add(value)
    return sorted(duplicated)


def _check_unique_ids(
    items: Any, *, label: str, errors: ErrorCollector, field: str = CONTENT
) -> None:
    """Deux entrees partageant un id rendent la solution ambigue."""
    if duplicated := _duplicates([item["id"] for item in _dicts(items) if "id" in item]):
        errors.add(field, f"{label} : ids en double ({duplicated})")


def _graph_node_types(content: Payload, *graph_keys: str) -> set[str]:
    """Types de nodes deja poses dans les graphes fournis par l'enonce."""
    types: set[str] = set()
    for key in graph_keys:
        value = content.get(key)
        if isinstance(value, dict):
            types |= {node["type"] for node in _dicts(value.get("nodes")) if "type" in node}
    return types


# ---------------------------------------------------------------------------
# 2. Integrite des graphes fournis
# ---------------------------------------------------------------------------
def check_graph_integrity(
    value: Any, *, label: str, field: str, errors: ErrorCollector
) -> None:
    """Un graphe d'enonce doit etre lisible tel quel.

    Deux nodes avec le meme id, ou une connexion vers un node absent, donnent un
    canvas incoherent cote frontend et un validateur qui compare n'importe quoi.
    """
    if not isinstance(value, dict):
        return

    node_ids = [node["id"] for node in _dicts(value.get("nodes")) if "id" in node]
    if duplicated := _duplicates(node_ids):
        errors.add(field, f"{label} : ids de nodes en double ({duplicated})")

    known = set(node_ids)
    dangling: set[str] = set()
    for edge in _dicts(value.get("edges")):
        for side in ("from", "to"):
            reference = edge.get(side)
            if reference is not None and reference not in known:
                dangling.add(reference)
    if dangling:
        errors.add(
            field,
            f"{label} : des connexions pointent vers des nodes inexistants "
            f"({sorted(dangling)})",
        )


# ---------------------------------------------------------------------------
# 3a. Faisabilite des exigences (types de production)
# ---------------------------------------------------------------------------
#: Le controle de faisabilite ne porte que sur les clauses positives :
#: interdire un node absent de la palette est inutile, mais pas faux.
#: Le controle de vocabulaire (catalogue), lui, porte sur tout.
_ALL_NODE_CLAUSES = ("required_nodes", "forbidden_nodes")
_ALL_EDGE_CLAUSES = ("required_edges", "forbidden_edges")


def _iter_node_selectors(
    solution: Payload, node_clauses: tuple[str, ...], edge_clauses: tuple[str, ...]
) -> list[tuple[str, Payload]]:
    """Tous les selecteurs de node d'une solution, avec leur origine.

    Un selecteur de connexion porte deux selecteurs de node (`from` et `to`) de
    la meme forme : on les traite exactement comme les autres.
    """
    selectors: list[tuple[str, Payload]] = []
    for clause in node_clauses:
        selectors += [(clause, selector) for selector in _dicts(solution.get(clause))]
    for clause in edge_clauses:
        for edge in _dicts(solution.get(clause)):
            for side in ("from", "to"):
                if isinstance(edge.get(side), dict):
                    selectors.append((f"{clause}.{side}", edge[side]))
    return selectors


def _check_requirements_reachable(
    exercise_type: str,
    content: Payload,
    solution: Payload,
    schema: ExerciseSchema,
    errors: ErrorCollector,
) -> None:
    """Chaque exigence doit porter sur quelque chose que l'eleve peut produire.

    Exiger un node absent de la palette ET du graphe fourni rend l'exercice
    insoluble ; exiger une variable jamais declaree revient au meme. C'est
    l'erreur d'auteur la plus frequente sur les types de production.
    """
    required = _iter_node_selectors(solution, ("required_nodes",), ("required_edges",))

    # Le type I n'a ni palette ni canvas : l'eleve travaille dans Unreal, ou
    # tout le catalogue lui est accessible. Son garde-fou est le vocabulaire,
    # verifie pour tous les types a l'etape precedente.
    if exercise_type != ExerciseType.UNREAL_EXPORT:
        palette_types = {
            item["type"] for item in _dicts(content.get("palette")) if "type" in item
        }
        available = palette_types | _graph_node_types(content, *schema.graph_keys)
        for origin, selector in required:
            if selector.get("type") not in available:
                errors.add(
                    SOLUTION,
                    f"{origin} : le node '{selector.get('type')}' n'est ni en "
                    "palette ni dans le graphe fourni ; l'exercice serait insoluble",
                )

    _check_selector_matches(content, required, errors)
    _check_required_variables(content, solution, errors)


def _check_selector_matches(
    content: Payload, selectors: list[tuple[str, Payload]], errors: ErrorCollector
) -> None:
    """Un `match` doit designer quelque chose qui existe dans l'enonce.

    Exiger un `Get` sur la variable « Health » alors que l'enonce ne declare
    aucune variable de ce nom produit un exercice impossible, exactement comme
    un node hors palette.
    """
    declared_variables = {
        variable["name"]
        for variable in _dicts(content.get("variables"))
        if "name" in variable
    }
    for origin, selector in selectors:
        match = selector.get("match")
        if not isinstance(match, dict):
            continue
        variable = match.get("variable")
        if variable and variable not in declared_variables:
            errors.add(
                SOLUTION,
                f"{origin} : le selecteur cible la variable '{variable}', "
                "absente de content.variables",
            )


def _check_required_variables(
    content: Payload, solution: Payload, errors: ErrorCollector
) -> None:
    """Une variable exigee doit exister dans l'enonce, avec le meme type."""
    declared = {
        variable["name"]: variable.get("type")
        for variable in _dicts(content.get("variables"))
        if "name" in variable
    }
    for requirement in _dicts(solution.get("required_variables")):
        name = requirement.get("name")
        if name not in declared:
            errors.add(
                SOLUTION,
                f"la variable requise '{name}' n'est declaree nulle part dans "
                "content.variables : l'eleve ne peut pas la produire",
            )
            continue
        expected, actual = requirement.get("type"), declared[name]
        if expected and actual and expected != actual:
            errors.add(
                SOLUTION,
                f"la variable '{name}' est exigee en '{expected}' mais declaree "
                f"en '{actual}' dans l'enonce",
            )


def _unknown_types(node_ids: set[str]) -> list[str]:
    return sorted(node_id for node_id in node_ids if not is_known_node_type(node_id))


def _catalog_hint(unknown: list[str]) -> str:
    return (
        f"types de nodes absents du catalogue : {unknown}. Verifier l'identifiant "
        "dans l'export UE5 (Class= / MemberName=), ou completer le catalogue via "
        "le reglage BLUEPRINT_EXTRA_NODE_TYPES."
    )


def check_catalog_vocabulary(
    content: Payload, solution: Payload, schema: ExerciseSchema, errors: ErrorCollector
) -> None:
    """Tout node designe, ou qu'il soit, doit exister dans le catalogue.

    Le catalogue est le vocabulaire unique de la plateforme (CLAUDE.md) : un
    identifiant invente rendrait le node impossible a dessiner sur le canvas et
    impossible a reconnaitre dans un export Unreal.
    """
    # Palette : identifiant connu, et libelle conforme a celui de l'editeur.
    palette_unknown: set[str] = set()
    for item in _dicts(content.get("palette")):
        node_type = item.get("type")
        if not node_type:
            continue
        node = get_node_type(node_type)
        if node is None:
            palette_unknown.add(node_type)
        elif item.get("label") and item["label"] != node.label:
            errors.add(
                CONTENT,
                f"palette : le libelle '{item['label']}' ne correspond pas au nom "
                f"affiche par l'editeur pour {node_type} ('{node.label}')",
            )
    if palette_unknown:
        errors.add(CONTENT, "palette : " + _catalog_hint(sorted(palette_unknown)))

    # Graphes fournis par l'enonce, illustration des types de rappel comprise.
    for key in schema.graph_keys:
        value = content.get(key)
        if isinstance(value, dict):
            unknown = _unknown_types(
                {node["type"] for node in _dicts(value.get("nodes")) if "type" in node}
            )
            if unknown:
                errors.add(CONTENT, f"{key} : " + _catalog_hint(unknown))

    # Graphe de reference, cote solution.
    reference = solution.get("reference_graph")
    if isinstance(reference, dict):
        unknown = _unknown_types(
            {node["type"] for node in _dicts(reference.get("nodes")) if "type" in node}
        )
        if unknown:
            errors.add(SOLUTION, "reference_graph : " + _catalog_hint(unknown))

    # Selecteurs, clauses negatives comprises : une faute de frappe dans un
    # `forbidden_*` rendrait la clause silencieusement inoperante.
    unknown = _unknown_types(
        {
            selector["type"]
            for _, selector in _iter_node_selectors(
                solution, _ALL_NODE_CLAUSES, _ALL_EDGE_CLAUSES
            )
            if selector.get("type")
        }
    )
    if unknown:
        errors.add(SOLUTION, _catalog_hint(unknown))


# ---------------------------------------------------------------------------
# 3b. Controles specifiques a un type
# ---------------------------------------------------------------------------
def _check_mcq(content: Payload, solution: Payload, errors: ErrorCollector) -> None:
    _check_unique_ids(content.get("options"), label="options", errors=errors)

    option_ids = _ids(content.get("options"))
    correct = solution.get("correct_option_ids", [])
    if unknown := set(correct) - option_ids:
        errors.add(
            SOLUTION,
            f"correct_option_ids reference des options inexistantes : {sorted(unknown)}",
        )
    if not content.get("multiple") and len(correct) > 1:
        errors.add(
            SOLUTION, "plusieurs bonnes reponses declarees alors que multiple vaut false"
        )
    if unknown_explained := set(solution.get("option_explanations", {})) - option_ids:
        errors.add(
            SOLUTION,
            "option_explanations reference des options inexistantes : "
            f"{sorted(unknown_explained)}",
        )


def _check_ordering(content: Payload, solution: Payload, errors: ErrorCollector) -> None:
    _check_unique_ids(content.get("items"), label="items", errors=errors)

    item_ids = _ids(content.get("items"))
    order = list(solution.get("order", []))
    if unknown := set(order) - item_ids:
        errors.add(SOLUTION, f"order reference des items inexistants : {sorted(unknown)}")
    if missing := item_ids - set(order):
        errors.add(SOLUTION, f"items absents de order : {sorted(missing)}")


def _check_node_matching(
    content: Payload, solution: Payload, errors: ErrorCollector
) -> None:
    _check_unique_ids(content.get("left"), label="left", errors=errors)
    _check_unique_ids(content.get("right"), label="right", errors=errors)

    left_ids, right_ids = _ids(content.get("left")), _ids(content.get("right"))
    pairs = _dicts(solution.get("pairs"))

    for pair in pairs:
        if pair.get("left_id") not in left_ids:
            errors.add(SOLUTION, f"pair.left_id inconnu : {pair.get('left_id')}")
        if pair.get("right_id") not in right_ids:
            errors.add(SOLUTION, f"pair.right_id inconnu : {pair.get('right_id')}")

    paired = [pair["left_id"] for pair in pairs if "left_id" in pair]
    if duplicated := _duplicates(paired):
        errors.add(
            SOLUTION,
            f"chaque element de gauche doit avoir une seule cible ; en double : "
            f"{duplicated}",
        )
    if unpaired := left_ids - set(paired):
        errors.add(SOLUTION, f"elements de gauche sans association : {sorted(unpaired)}")


def _check_locked_nodes(
    content: Payload, graph_key: str, errors: ErrorCollector
) -> None:
    value = content.get(graph_key)
    node_ids = _ids(value.get("nodes")) if isinstance(value, dict) else set()
    if unknown := set(content.get("locked_node_ids", [])) - node_ids:
        errors.add(CONTENT, f"locked_node_ids absents du graphe : {sorted(unknown)}")


def _check_debugging(
    content: Payload, solution: Payload, errors: ErrorCollector
) -> None:
    _check_locked_nodes(content, "broken_graph", errors)
    # TODO(Phase 2b) : verifier aussi que le graphe casse ne satisfait pas deja
    # la solution (voir le TODO en bas de module).
    if not any(
        solution.get(key)
        for key in ("forbidden_nodes", "forbidden_edges", "required_edges")
    ):
        errors.add(
            SOLUTION,
            "un exercice de debugging doit dire ce qui doit DISPARAITRE ou etre "
            "reconnecte (forbidden_nodes, forbidden_edges ou required_edges)",
        )


def _check_graph_complete(
    content: Payload, solution: Payload, errors: ErrorCollector
) -> None:
    del solution
    _check_locked_nodes(content, "partial_graph", errors)


def _check_unreal_export(
    content: Payload, solution: Payload, errors: ErrorCollector
) -> None:
    """Le texte colle depuis Unreal ne restitue que des nodes et des connexions."""
    del content
    if not solution.get("required_nodes") and not solution.get("required_edges"):
        errors.add(
            SOLUTION,
            "un exercice de type I doit exiger au moins un node ou une connexion : "
            "c'est tout ce que le texte colle depuis Unreal permet de verifier",
        )


# ---------------------------------------------------------------------------
# Registre
# ---------------------------------------------------------------------------
EXERCISE_SCHEMAS: dict[str, ExerciseSchema] = {
    # --- Rappel et transition (le graphe n'est qu'une illustration)
    ExerciseType.QUESTION: ExerciseSchema(
        interactive.QUESTION_CONTENT,
        interactive.QUESTION_SOLUTION,
        graph_keys=("graph",),
    ),
    ExerciseType.MCQ: ExerciseSchema(
        interactive.MCQ_CONTENT,
        interactive.MCQ_SOLUTION,
        graph_keys=("graph",),
        coherence=_check_mcq,
    ),
    ExerciseType.ORDERING: ExerciseSchema(
        interactive.ORDERING_CONTENT,
        interactive.ORDERING_SOLUTION,
        graph_keys=("graph",),
        coherence=_check_ordering,
    ),
    ExerciseType.NODE_MATCHING: ExerciseSchema(
        interactive.NODE_MATCHING_CONTENT,
        interactive.NODE_MATCHING_SOLUTION,
        coherence=_check_node_matching,
    ),
    # --- Production
    ExerciseType.GRAPH_BUILD: ExerciseSchema(
        graph.GRAPH_BUILD_CONTENT,
        graph.GRAPH_BUILD_SOLUTION,
        graph_keys=("initial_graph",),
    ),
    ExerciseType.DEBUGGING: ExerciseSchema(
        graph.DEBUGGING_CONTENT,
        graph.DEBUGGING_SOLUTION,
        graph_keys=("broken_graph",),
        coherence=_check_debugging,
    ),
    ExerciseType.CHALLENGE: ExerciseSchema(
        graph.CHALLENGE_CONTENT,
        graph.CHALLENGE_SOLUTION,
        graph_keys=("initial_graph",),
    ),
    ExerciseType.GRAPH_COMPLETE: ExerciseSchema(
        graph.GRAPH_COMPLETE_CONTENT,
        graph.GRAPH_COMPLETE_SOLUTION,
        graph_keys=("partial_graph",),
        coherence=_check_graph_complete,
    ),
    ExerciseType.UNREAL_EXPORT: ExerciseSchema(
        graph.UNREAL_EXPORT_CONTENT,
        graph.UNREAL_EXPORT_SOLUTION,
        coherence=_check_unreal_export,
    ),
}


def get_exercise_schema(exercise_type: str) -> ExerciseSchema:
    try:
        return EXERCISE_SCHEMAS[exercise_type]
    except KeyError as exc:
        raise ValidationError(
            {"type": f"Type d'exercice inconnu : {exercise_type!r}."}
        ) from exc


def validate_exercise_payload(exercise_type: str, content: Any, solution: Any) -> None:
    """Valide `content` et `solution` pour un type donne.

    Leve une `ValidationError` Django dont les cles correspondent aux champs du
    modele, pour que l'admin et DRF affichent l'erreur au bon endroit.
    """
    schema = get_exercise_schema(exercise_type)
    content = content or {}
    solution = solution or {}

    # 1. Forme. Inutile d'aller plus loin si elle est fausse : les controles
    # suivants supposent une structure exploitable.
    shape_errors: FieldErrors = {}
    for field, payload, field_schema in (
        (CONTENT, content, schema.content),
        (SOLUTION, solution, schema.solution),
    ):
        try:
            validate_against_schema(payload, field_schema, label=field)
        except ValidationError as exc:
            shape_errors[field] = exc.messages
    if shape_errors:
        raise ValidationError(shape_errors)

    errors = ErrorCollector()

    # 2. Integrite de chaque graphe fourni par l'enonce, et du graphe de
    # reference eventuellement joint a la solution.
    for key in schema.graph_keys:
        check_graph_integrity(content.get(key), label=key, field=CONTENT, errors=errors)
    check_graph_integrity(
        solution.get("reference_graph"),
        label="reference_graph",
        field=SOLUTION,
        errors=errors,
    )

    # 2b. Vocabulaire : le catalogue est la reference unique, pour tous les
    # types - un graphe d'illustration ne peut pas inventer un node non plus.
    check_catalog_vocabulary(content, solution, schema, errors)

    # 3a. Les exigences doivent etre realisables.
    if exercise_type in GRAPH_BASED_TYPES:
        _check_requirements_reachable(exercise_type, content, solution, schema, errors)

    # 3b. Controles propres au type.
    if schema.coherence is not None:
        schema.coherence(content, solution, errors)

    if errors:
        raise ValidationError(errors.as_dict())


# ---------------------------------------------------------------------------
# TODO(Phase 2b) - a brancher des que le validateur de graphe existera
# ---------------------------------------------------------------------------
# Refuser a la sauvegarde un exercice F (debugging) ou H (completer) dont le
# graphe de depart satisfait DEJA la solution : l'eleve le reussirait sans rien
# faire. C'est l'erreur d'auteur la plus couteuse, parce qu'elle est invisible a
# la relecture - le contenu semble correct, seul le comportement est faux.
#
# Implementation prevue, une fois `apps.validation` en place :
#
#     from apps.validation.services import get_validator
#
#     def _reject_already_solved(exercise_type, content, solution, errors):
#         graph_key = {"F": "broken_graph", "H": "partial_graph"}[exercise_type]
#         result = get_validator(exercise_type).validate_graph(
#             solution, content.get(graph_key) or {"nodes": [], "edges": []}
#         )
#         if result.is_correct:
#             errors.add(CONTENT, f"{graph_key} satisfait deja la solution : "
#                                 "l'exercice serait reussi sans modification")
#
# A appeler depuis `validate_exercise_payload`, apres l'etape 3b. L'import doit
# rester LOCAL a la fonction : `apps.validation` est une app isolee, et
# `apps.exercises.schemas` est importe au chargement des modeles.
