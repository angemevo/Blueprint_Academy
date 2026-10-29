"""Verification d'un graphe soumis contre les exigences d'une `solution` (E, G).

La solution decrit des PROPRIETES, jamais un graphe exact (voir
`schemas/graph.py`). Fonctions pures, sans acces base ni import de
`apps.validation` : le validateur du registre s'en sert.

Regles :
- un selecteur designe un node par `type` (identifiant du catalogue) et un
  `match` optionnel : egalite exacte, sensible a la casse, sur toutes les
  proprietes citees ;
- une exigence positive est remplie si au moins un node (ou un couple) la
  satisfait ; `min_count` demande davantage de nodes ;
- score = part des exigences positives remplies (0 a 100) ; une exigence
  negative violee (`forbidden_*`, `max_nodes`) rend l'exercice incorrect et
  plafonne le score a `MAX_SCORE - 1`.
"""

from dataclasses import dataclass, field
from typing import Any

MAX_SCORE = 100


@dataclass
class GraphVerdict:
    score: int
    is_correct: bool
    feedback: list[str] = field(default_factory=list)


class MalformedGraph(ValueError):
    """La soumission n'est pas un graphe normalise."""


def _nodes(graph: Any) -> tuple[list[dict], list[dict], list[dict]]:
    if not isinstance(graph, dict):
        raise MalformedGraph
    nodes, edges = graph.get("nodes"), graph.get("edges")
    variables = graph.get("variables", [])
    for items in (nodes, edges, variables):
        if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
            raise MalformedGraph
    for node in nodes:
        if not isinstance(node.get("id"), str) or not isinstance(node.get("type"), str):
            raise MalformedGraph
    return nodes, edges, variables


def node_matches(node: dict, selector: dict) -> bool:
    if node.get("type") != selector["type"]:
        return False
    properties = node.get("properties")
    properties = properties if isinstance(properties, dict) else {}
    return all(
        key in properties and properties[key] == value
        for key, value in selector.get("match", {}).items()
    )


def _edge_matches(edge: dict, selector: dict, by_id: dict[str, dict]) -> bool:
    start, end = by_id.get(edge.get("from")), by_id.get(edge.get("to"))
    if start is None or end is None:
        return False
    for pin in ("from_pin", "to_pin"):
        if pin in selector and edge.get(pin) != selector[pin]:
            return False
    return node_matches(start, selector["from"]) and node_matches(end, selector["to"])


def _node_count(nodes: list[dict], selector: dict) -> int:
    return sum(1 for node in nodes if node_matches(node, selector))


def _has_edge(edges: list[dict], selector: dict, by_id: dict[str, dict]) -> bool:
    return any(_edge_matches(edge, selector, by_id) for edge in edges)


def check_graph(graph: Any, solution: dict) -> GraphVerdict:
    """Compare `graph` a `solution` ; leve `MalformedGraph` si le format est invalide."""
    nodes, edges, variables = _nodes(graph)
    by_id = {node["id"]: node for node in nodes}
    declared = {(v.get("name"), v.get("type")) for v in variables}

    # (categorie, rempli) pour chaque exigence positive.
    checks: list[tuple[str, bool]] = []
    for req in solution.get("required_nodes", []):
        needed = req.get("min_count", 1)
        checks.append(("nodes", _node_count(nodes, req) >= needed))
    for req in solution.get("required_edges", []):
        checks.append(("connexions", _has_edge(edges, req, by_id)))
    for req in solution.get("required_variables", []):
        checks.append(("variables", (req["name"], req["type"]) in declared))

    violations: list[str] = []
    if any(_node_count(nodes, sel) for sel in solution.get("forbidden_nodes", [])):
        violations.append("Un node interdit par l'énoncé est utilisé.")
    if any(_has_edge(edges, sel, by_id) for sel in solution.get("forbidden_edges", [])):
        violations.append("Une connexion interdite par l'énoncé est présente.")
    max_nodes = solution.get("max_nodes")
    if max_nodes is not None and len(nodes) > max_nodes:
        violations.append(f"Ton graphe dépasse la limite de {max_nodes} nodes.")

    satisfied = sum(1 for _, ok in checks if ok)
    score = satisfied * MAX_SCORE // len(checks) if checks else 0
    if violations:
        score = min(score, MAX_SCORE - 1)

    feedback = list(violations)
    for category in ("nodes", "connexions", "variables"):
        missing = sum(1 for cat, ok in checks if cat == category and not ok)
        if missing:
            feedback.append(f"Il manque des éléments du côté des {category} ({missing}).")
    is_correct = score == MAX_SCORE and not violations
    if is_correct:
        feedback = ["Le graphe répond à toutes les exigences."]
    return GraphVerdict(score=score, is_correct=is_correct, feedback=feedback)
