# Roadmap

Tenue par l'orchestrateur. Ange valide les changements de priorité. Source : section « Roadmap » de `CLAUDE.md`.

Mise à jour : 2026-10-16 (pilotage S42). L'état GitHub n'a pas pu être lu ce jour-là (accès `gh` refusé) ; cette roadmap repose sur `issues/` et `state/`.

## Phase en cours : 2b, services, validateurs et API (MVP / P0)

### En cours
- Rien. Aucune issue n'est `ready`, aucune PR n'a été ouverte par l'équipe.

### Prêt à démarrer dès qu'Ange pose `ready` (pas de dépendance)
1. Outillage qualité (ruff, ESLint) : `issues/01`, présumée #1
2. Interfaces de validation et registre : `issues/02`, présumée #2
3. Authentification JWT : `issues/05`, présumée #5 (question blacklist à trancher avant)

### Ensuite, dans l'ordre des dépendances
- Chaîne validation : Interfaces (02) → Validateurs A, B, C, D (03) → Soumission (09) → XP et niveaux (10)
- Chaîne API : Auth (05) → Profil et permissions (06) → API catalogue (07) → API exercices (08) → Soumission (09)
- Chemin critique : la chaîne API (4 issues avant la soumission). Au rythme de 2 issues par semaine, il faut faire avancer les deux chaînes en parallèle dès que possible.

### À cadrer par Ange avant délégation (`a-cadrer`)
- Moteur de validation de graphe (E, F, G, H) : `issues/04`
- Calcul de la maîtrise des skills : `issues/11`
- Pas encore d'issue : normalisation de l'export UE5 pour le type I (citée « issue séparée » dans `issues/04`, prévue au P0)

## Fait
- Phase 1 : architecture et configuration
- Phase 2a : modèle de données, taxonomie A–I, validation de contenu

## Plus tard (ne pas anticiper)
- Phase 3 : frontend applicatif (canvas React Flow)
- Phases 4 à 8 : admin, seed, tests, Docker, documentation
- P1, V2, V3, V4 : voir `CLAUDE.md`
