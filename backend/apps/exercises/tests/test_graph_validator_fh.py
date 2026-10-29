"""Validateur de graphe F/H : nodes verrouilles et refus a la sauvegarde.

Graphes SYNTHETIQUES : noms de pins et proprietes a verifier dans Unreal.
"""

from types import SimpleNamespace

import pytest
from django.core.exceptions import ValidationError

from apps.exercises.schemas import validate_exercise_payload
from apps.exercises.validators import get_validator

BEGIN = "K2Node_Event:ReceiveBeginPlay"
PRINT = "K2Node_CallFunction:PrintString"
BRANCH = "K2Node_IfThenElse"
PALETTE = [{"type": BEGIN}, {"type": PRINT}, {"type": BRANCH}]
WIRE = {"from": {"type": BEGIN}, "to": {"type": PRINT}, "from_pin": "then", "to_pin": "execute"}  # a verifier dans Unreal
SOLUTION = {"required_nodes": [{"type": PRINT}], "required_edges": [WIRE]}


def n(id_, type_, **props):
    return {"id": id_, "type": type_, "properties": props, "position": {"x": 0, "y": 0}}


def e(a, b):
    return {"from": a, "to": b, "from_pin": "then", "to_pin": "execute"}


def run(t, content, graph, solution=SOLUTION):
    ex = SimpleNamespace(type=t, content=content, solution=solution)
    return get_validator(t).validate(ex, graph)


H_CONTENT = {
    "prompt": "p", "palette": PALETTE, "locked_node_ids": ["b"],
    "partial_graph": {"nodes": [n("b", BEGIN)], "edges": []},
}
F_CONTENT = {
    "prompt": "p", "palette": PALETTE, "locked_node_ids": ["b"],
    "broken_graph": {"nodes": [n("b", BEGIN), n("p", PRINT)], "edges": [e("b", "p")]},
}


def test_h_good_node_and_edge_is_100():
    g = {"nodes": [n("b", BEGIN), n("p", PRINT)], "edges": [e("b", "p")]}
    r = run("H", H_CONTENT, g)
    assert (r.score, r.is_correct) == (100, True)


def test_h_node_without_edge_is_partial_and_incorrect():
    r = run("H", H_CONTENT, {"nodes": [n("b", BEGIN), n("p", PRINT)], "edges": []})
    assert 0 < r.score < 100 and not r.is_correct


def test_f_fixed_by_changing_a_connection_is_100():
    content = {**F_CONTENT, "broken_graph": {
        "nodes": [n("b", BEGIN), n("p", PRINT), n("x", BRANCH)], "edges": [e("b", "x")]}}
    fixed = {"nodes": content["broken_graph"]["nodes"], "edges": [e("b", "p")]}
    assert run("F", content, content["broken_graph"]).score < 100
    assert run("F", content, fixed).score == 100


def test_locked_node_removed_scores_zero_without_leaking_solution():
    r = run("H", H_CONTENT, {"nodes": [n("p", PRINT)], "edges": []})
    assert r.score == 0 and not r.is_correct
    assert "b" in r.feedback[0] and "supprimé" in r.feedback[0]
    assert "execute" not in " ".join(r.feedback)


def test_locked_node_modified_scores_zero():
    content = {**H_CONTENT, "partial_graph": {"nodes": [n("b", BEGIN, note="x")], "edges": []}}
    r = run("H", content, {"nodes": [n("b", BEGIN, note="y"), n("p", PRINT)], "edges": [e("b", "p")]})
    assert r.score == 0 and "modifié" in r.feedback[0]
    r = run("H", H_CONTENT, {"nodes": [n("b", PRINT), n("p", PRINT)], "edges": []})
    assert r.score == 0


def test_locked_node_moved_is_accepted():
    moved = n("b", BEGIN)
    moved["position"] = {"x": 500, "y": 80}
    r = run("H", H_CONTENT, {"nodes": [moved, n("p", PRINT)], "edges": [e("b", "p")]})
    assert r.score == 100 and r.is_correct


@pytest.mark.parametrize("t,content", [("F", {**F_CONTENT, "broken_graph": {
    "nodes": [n("b", BEGIN), n("p", PRINT)], "edges": [e("b", "p")]}}),
    ("H", {**H_CONTENT, "partial_graph": {
        "nodes": [n("b", BEGIN), n("p", PRINT)], "edges": [e("b", "p")]}})])
def test_already_solved_start_graph_is_refused_on_save(t, content):
    with pytest.raises(ValidationError) as caught:
        validate_exercise_payload(t, content, SOLUTION)
    assert "content" in caught.value.message_dict


def test_unsolved_start_graph_is_accepted_on_save():
    validate_exercise_payload("H", H_CONTENT, SOLUTION)
