"""Couche service de l'app validation (isolee du reste du domaine).

Points d'extension prevus par CLAUDE.md, implementes en Phase 2 :

- `Validator.validate(exercise, submission) -> ValidationResult`
  avec `ValidationResult(is_correct, score, feedback, hints)` ;
- validation par proprietes du graphe normalise (types E et G) :
  `{"nodes": [{"id", "type"}], "edges": [{"from", "to", "pin"}]}` ;
  on verifie la presence de nodes / connexions / variables / types,
  jamais une egalite stricte de graphe ;
- `HintService` (indices progressifs), prise ou se greffera le tuteur IA en V2.
"""
