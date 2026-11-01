# Roadmap

Tenue par l'orchestrateur. Source : section « Roadmap » de `CLAUDE.md`.

Mise à jour : 2026-10-20 (pilotage S43). Lu sur GitHub : issues #1 à #16, PR #12 mergée, PR #13 et #14 ouvertes.

## Phase en cours : 2b, services, validateurs et API (MVP / P0)

### Fait
- #1 Outillage qualité (PR #12)

### En cours
- #2 Interfaces de validation (PR #14, approuvée, en brouillon)
- #15 Typecheck frontend, #5 Auth JWT, #16 Épingler ruff (`ready`, plan S44)

### Ensuite, dans l'ordre des dépendances
- Chaîne API : #5 → #6 → #7 → #8 → #9 (une issue par semaine environ)
- Chaîne validation : #2 → #3 → #9
- Puis #9 → #10 XP et niveaux

### À cadrer par Ange (`a-cadrer`)
- #4 Moteur de validation de graphe (proposition de l'équipe en commentaire, Q3)
- #11 Maîtrise des skills (Q4)
- Type I (import Unreal) : reporté en V3 ou V4 (décision d’Ange, 2026-10-25), hors MVP

## Fait
- Phase 1 : architecture et configuration
- Phase 2a : modèle de données, taxonomie A–I, validation de contenu

## Plus tard (ne pas anticiper)
- Phase 3 : frontend applicatif (canvas React Flow)
- Phases 4 à 8 : admin, seed, tests, Docker, documentation
- P1, V2, V3, V4 : voir `CLAUDE.md`

## Mise à jour 2026-11-01 (pilotage S44)
- Phase 3 (écrans du site) : terminée. Phase 2b : terminée (#4 reste ouverte pour la validation par Ange des cas « à vérifier dans Unreal »).
- Phase en cours : 4, administration. En cours : #61 (admin de contenu), puis #62 (publication avec contrôle d'intégrité).
- Ensuite : phase 5 (parcours de départ, attend Ange, Q2), 6 tests de bout en bout, 7 Docker, 8 documentation. Ne pas anticiper sans accord.
