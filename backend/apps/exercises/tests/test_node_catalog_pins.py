import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from common.blueprint_catalog import (
    PIN_DIRECTIONS,
    PIN_TYPES,
    known_node_types,
)


def test_pins_valides():
    avec_pins = 0
    for node in known_node_types().values():
        names = [p.name for p in node.pins]
        assert len(names) == len(set(names)), node.id
        for pin in node.pins:
            assert pin.type in PIN_TYPES, (node.id, pin)
            assert pin.direction in PIN_DIRECTIONS, (node.id, pin)
        avec_pins += bool(node.pins)
    assert avec_pins >= 10


def test_ids_inchanges():
    nodes = known_node_types()
    assert "K2Node_Event:ReceiveBeginPlay" in nodes
    assert "K2Node_CallFunction:PrintString" in nodes


@pytest.mark.django_db
def test_endpoint():
    url = "/api/node-catalog/"
    assert APIClient().get(url).status_code == 401
    user = get_user_model().objects.create_user(
        username="u1", email="u1@example.com", password="x-Passw0rd!"
    )
    client = APIClient()
    client.force_authenticate(user)
    data = client.get(url).json()
    assert len(data) == len({n["id"] for n in data})
    branch = next(n for n in data if n["id"] == "K2Node_IfThenElse")
    assert branch["label"] == "Branch"
    assert {"name", "label", "direction", "type"} == set(branch["pins"][0])
    assert "solution" not in str(data)
