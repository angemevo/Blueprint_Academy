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
