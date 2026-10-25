"""Lecture du catalogue de nodes pour le canvas (pas de solution, pas de doublon)."""

from common.blueprint_catalog import known_node_types


def serialize_node_catalog() -> list[dict]:
    """Liste des nodes : id, libelle, categorie et pins."""
    return [
        {
            "id": node.id,
            "label": node.label,
            "category": node.category,
            "pins": [
                {"name": p.name, "label": p.label, "direction": p.direction, "type": p.type}
                for p in node.pins
            ],
        }
        for node in known_node_types().values()
    ]
