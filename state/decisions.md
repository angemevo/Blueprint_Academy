# Journal des décisions

Format : `AAAA-MM-JJ — décision — raison — qui (Ange / agent)`

Les décisions d'architecture et de produit verrouillées sont dans `CLAUDE.md` ; ce journal ne trace que les décisions prises pendant le travail de l'équipe d'agents.

- 2026-10-15 — Blueprint Academy sert de projet pilote pour l'équipe d'agents — projet existant, cadré, sans validation de marché préalable — Ange
- 2026-10-15 — Phase 1 de l'équipe : pôle Tech seul ; Ange merge toutes les PR — prouver la fiabilité avant d'automatiser — Ange
- 2026-10-15 — 2 issues par semaine au maximum au départ — deux bases de code, quota Claude Pro partagé — Ange
- 2026-10-20 — Blacklist JWT activée (`token_blacklist`, `BLACKLIST_AFTER_ROTATION = True`) pour #5 — réglage de sécurité dans la stack verrouillée, réversible ; un refresh volé ou déconnecté n'est plus réutilisable — agent (orchestrateur)
- 2026-10-20 — Typecheck frontend cassé : issue #15 `ready` (retirer `.next/dev/types` de l'analyse) — la PR #13 ne corrige pas le problème (elle ne touche que le lockfile) — agent
- 2026-10-20 — Épingler ruff sur une version mineure : issue #16 `ready` — lint reproductible pour le portier — agent
- 2026-10-20 — Règle de score de #3, courbe de niveaux de #10, cadrage de #4 : renvoyés à Ange (Q1 à Q3), choix pédagogiques ou à vérifier dans Unreal — agent
- 2026-10-15 — Le moteur de validation de graphe et la formule de maîtrise sont cadrés par Ange avant délégation — cœur pédagogique, risque n° 1 du projet — Ange
- 2026-10-22 — Étiquette ready posée sur #6, #7, #8 (dépendances mergées ou traitées plus tôt la même nuit) — agent (chef d'équipe)
- 2026-10-23 — Q2 : principe de la courbe de niveaux par liste de seuils validé ; valeurs de départ proposées avant #9 — Ange
- 2026-10-23 — Q4 : principe de maîtrise : réussir sans erreur, en moins de temps que la moyenne, avec peu de tentatives ; formule chiffrée à rédiger par l'équipe puis à valider par Ange — Ange
- 2026-10-23 — Q5 : option A (issue du type I en `a-cadrer`, à créer au prochain pilotage) ; Ange fournit des exports Unreal le samedi 24 octobre — Ange
- 2026-10-23 — Q1 (« A et B », contradictoire) et Q3 (cadrage non validé explicitement) : reposées à Ange — agent

- 2026-10-23 — Q1 : option A, score partiel pour les exercices C et D (ordre et paires) ; #3 `ready` (#2 mergée via la PR #14) — Ange
- 2026-10-23 — Q3 : cadrage du moteur de validation de graphe (#4) validé tel que proposé (option A) ; cas de test encore « à vérifier dans Unreal », #4 reste `a-cadrer` jusqu'aux exports du 24 octobre — Ange

## 2026-10-23 - Validateurs A/B/C/D (#3)
- Barème appliqué comme proposé dans l'issue : A et B tout-ou-rien ; C = part des éléments bien placés ; D = part des paires correctes (plafonné à 99 s'il y a des paires en trop). Format de soumission choisi : A `{"answer"}`, B `{"selected_option_ids"}`, C `{"order"}`, D `{"pairs":[{left_id,right_id}]}`. Chargement des validateurs dans `ExercisesConfig.ready()`.

- 2026-10-23 (#10) : courbe XP_LEVEL_THRESHOLDS = 0,100,250,450,700,1000,1350,1750,2200,2700 (niveaux 1-10), réglage env modifiable ; principe validé par Ange (Q2).

- 2026-10-25 — Q6 : passage à la phase 3 (écrans du site) accepté ; issues #31 à #34 créées `ready` — Ange
- 2026-10-25 — Q7 : formule de maîtrise proposée en commentaire de #11 validée ; #11 `ready` — Ange
