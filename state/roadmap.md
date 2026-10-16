# Roadmap

Tenue par l'orchestrateur. Ange valide les changements de priorité. Source : section « Roadmap » de `CLAUDE.md`.

Mise à jour : 2026-10-16 (pilotage S42, 3e cycle). État lu sur GitHub : #1 à #11 ouvertes, `ready` sur #1 et #2 seulement, aucune PR.

## Phase en cours : 2b, services, validateurs et API (MVP / P0)

### Fait (phase 2b)
- Rien : aucune issue fermée, aucune PR.

### En cours (plan S42)
- #1 Outillage qualité (ruff, ESLint)
- #2 Interfaces de validation et registre

### Ensuite, dans l'ordre des dépendances
- Chaîne API (chemin critique, 5 issues jusqu'à la soumission) : #5 Auth → #6 Profil et permissions → #7 API catalogue → #8 API exercices → #9 Soumission
- Chaîne validation : #2 Interfaces → #3 Validateurs A, B, C, D → #9 Soumission
- Puis : #9 Soumission → #10 XP et niveaux
- Une issue n'entre au plan que si ses dépendances sont mergées : la chaîne API avance donc d'au plus une issue par semaine. Ordre recommandé : S43 #5 + #3, S44 #6, S45 #7, S46 #8, S47 #9, S48 #10. Il reste une place libre en S44, S45 et S46 : #4 pourra la prendre une fois cadrée.
- Condition pour démarrer S43 : la blacklist JWT (#5) et la règle de score (#3) sont tranchées, et `ready` est posé sur ces deux issues.

### À cadrer par Ange avant délégation (`a-cadrer`)
- #4 Moteur de validation de graphe (E, F, G, H)
- #11 Calcul de la maîtrise des skills
- Pas encore d'issue : normalisation de l'export UE5 pour le type I (« issue séparée » citée dans #4, prévue au P0)

## Fait
- Phase 1 : architecture et configuration
- Phase 2a : modèle de données, taxonomie A–I, validation de contenu

## Plus tard (ne pas anticiper)
- Phase 3 : frontend applicatif (canvas React Flow)
- Phases 4 à 8 : admin, seed, tests, Docker, documentation
- P1, V2, V3, V4 : voir `CLAUDE.md`
