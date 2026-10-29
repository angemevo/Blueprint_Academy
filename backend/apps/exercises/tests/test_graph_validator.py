"""Validateur de graphe E/G. Graphes SYNTHETIQUES : noms de pins et proprietes
sont a verifier dans Unreal, et ne servent pas de reference pedagogique."""

from types import SimpleNamespace

import pytest

from apps.exercises.models import Exercise
from apps.exercises.services.submission import submit_exercise
from apps.exercises.validators import get_validator
from apps.progress.models import SkillMastery

EVENT = {"type": "K2Node_Event"}
SET_HP = {"type": "K2Node_VariableSet", "match": {"variable": "Health"}}
PRINT = {"type": "K2Node_CallFunction", "match": {"function": "PrintString"}}  # a verifier dans Unreal


def node(id_, type_, **props):
    return {"id": id_, "type": type_, "properties": props}


def edge(a, b, fp="then", tp="execute"):  # noms de pins a verifier dans Unreal
    return {"from": a, "to": b, "from_pin": fp, "to_pin": tp}


def sol(**kw):
    base = {"required_nodes": [EVENT, SET_HP], "required_edges": [
        {"from": EVENT, "to": SET_HP, "from_pin": "then", "to_pin": "execute"}]}
    base.update(kw)
    return base


def run(solution, graph, t="E"):
    ex = SimpleNamespace(type=t, content={}, solution=solution)
    return get_validator(t).validate(ex, graph)


GOOD = {"nodes": [node("a", "K2Node_Event"), node("b", "K2Node_VariableSet", variable="Health")],
        "edges": [edge("a", "b")]}
# Autre ordre des nodes, meme graphe logique.
GOOD_REORDERED = {"nodes": list(reversed(GOOD["nodes"])), "edges": GOOD["edges"]}


@pytest.mark.parametrize("graph", [GOOD, GOOD_REORDERED])
@pytest.mark.parametrize("t", ["E", "G"])
def test_two_valid_solutions_give_100(graph, t):
    r = run(sol(), graph, t)
    assert (r.score, r.is_correct) == (100, True)


def test_missing_edge_is_partial_and_incorrect():
    r = run(sol(), {"nodes": GOOD["nodes"], "edges": []})
    assert r.score == 66 and not r.is_correct
    assert any("connexions" in f for f in r.feedback)
    assert "Health" not in " ".join(r.feedback)  # ne donne pas la solution


def test_forbidden_node_caps_at_99():
    graph = {"nodes": GOOD["nodes"] + [node("c", "K2Node_Tick")], "edges": GOOD["edges"]}
    r = run(sol(forbidden_nodes=[{"type": "K2Node_Tick"}]), graph)
    assert r.score == 99 and not r.is_correct


def test_max_nodes_caps_at_99():
    r = run(sol(max_nodes=1), GOOD)
    assert r.score == 99 and not r.is_correct


def test_custom_variable_name_matched_only_when_required():
    other = {"nodes": [node("a", "K2Node_Event"), node("b", "K2Node_VariableSet", variable="Vie")],
             "edges": [edge("a", "b")]}
    generic = {"required_nodes": [{"type": "K2Node_VariableSet"}]}
    assert run(generic, other).score == 100
    assert run({"required_nodes": [SET_HP]}, other).score == 0
    assert run({"required_nodes": [SET_HP]}, GOOD).score == 100


def test_match_is_case_sensitive_and_needs_all_properties():
    g = {"nodes": [node("b", "K2Node_VariableSet", variable="health")], "edges": []}
    assert run({"required_nodes": [SET_HP]}, g).score == 0
    both = {"type": "K2Node_VariableSet", "match": {"variable": "Health", "value": 1}}
    assert run({"required_nodes": [both]}, GOOD).score == 0


@pytest.mark.parametrize("kind", ["int", "double"])
def test_promoted_operator_same_identifier_whatever_the_wires(kind):
    add = {"type": "K2Node_PromotableOperator", "match": {"operation": "Add"}}  # a verifier dans Unreal
    g = {"nodes": [node("p", "K2Node_PromotableOperator", operation="Add", resolved=kind)], "edges": []}
    assert run({"required_nodes": [add]}, g).score == 100


def test_required_variables_and_min_count():
    s = {"required_variables": [{"name": "Health", "type": "float"}],
         "required_nodes": [{"type": "K2Node_Event", "min_count": 2}]}
    g = {"nodes": [node("a", "K2Node_Event")], "edges": [],
         "variables": [{"name": "Health", "type": "float"}]}  # declaree, jamais utilisee
    assert run(s, g).score == 50
    g["variables"][0]["type"] = "int"
    assert run(s, g).score == 0


@pytest.mark.parametrize("bad", [None, [], {"nodes": "x", "edges": []}, {"nodes": [{"id": 1}], "edges": []}])
def test_malformed_submission_scores_zero(bad):
    r = run(sol(), bad)
    assert r.score == 0 and not r.is_correct


@pytest.mark.django_db
def test_submission_moves_mastery():
    from apps.learning.models import Skill
    from apps.users.models import User

    skill = Skill.objects.create(name="Variables", slug="variables")
    user = User.objects.create_user(username="u", password="x")
    from apps.exercises.tests.test_exercise_api import PRINT as PRINT_ID
    from apps.exercises.tests.test_exercise_api import SPECS

    content, solution = SPECS["E"]
    e = Exercise.objects.create(type="E", title="E", slug="e-graph", is_published=True,
                                content=content, solution=solution)
    e.skills.add(skill)
    graph = {"nodes": [node("p", PRINT_ID)], "edges": []}
    attempt, result = submit_exercise(user, e, graph)
    assert result.is_correct and attempt.is_correct
    assert SkillMastery.objects.filter(user=user, skill=skill).exists()
