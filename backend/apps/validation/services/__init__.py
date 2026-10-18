"""Couche service de l'app validation (isolee du reste du domaine).

Les contrats sont declares dans `apps.validation.interfaces` :
`ValidationResult`, `Validator` et `HintService` (protocole seul, tuteur IA en
V2). Le registre `exercise_type -> Validator` vit dans
`apps.exercises.validators`.

A venir : validation par proprietes du graphe normalise (types E a I) :
`{"nodes": [{"id", "type"}], "edges": [{"from", "to", "from_pin", "to_pin"}]}` ;
on verifie la presence de nodes / connexions / variables / types, jamais une
egalite stricte de graphe.
"""
