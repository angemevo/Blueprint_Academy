# Questions pour Ange

Tenu par l'organisateur. Seules les questions qui reviennent à Ange y figurent (voir « Qui décide quoi » dans `.claude/equipe.md`), chacune avec options, recommandation et date. Elles sont posées à Ange dans son bureau (rapport du dimanche et rapport du matin), où il répond en commentaire.

Mise à jour : pilotage du 2026-10-20 (semaine 2026-S43). Aucune réponse d'Ange trouvée : aucun point hebdo n'avait encore été publié.

## En attente

- [ ] **Q1 — Règle de score des exercices de rappel et de transition (#3).** Ta réponse « A et B » est contradictoire (A : score partiel pour C et D ; B : tout ou rien pour C et D). Options : A : score partiel pour l'ordre et les paires ; B : tout ou rien partout. Recommandation : A. Sans réponse le 2026-10-25 : A appliquée, `ready` posé sur #3 dès que #2 est mergée.
- [ ] **Q3 — Cadrage du moteur de validation de graphe (#4).** Ta réponse parle des exports, pas du cadrage lui-même. Options : A : valider le cadrage proposé en commentaire de #4 ; B : le modifier. Recommandation : A. Pas d'application par défaut (vérification Unreal) : #4 reste `a-cadrer`. Les exports du samedi 24 octobre serviront aux cas de test.
- [ ] **Q4bis — Formule de maîtrise (#11).** Principe reçu d'Ange : maîtrise = réussir sans erreur, plus vite que la moyenne, avec le moins de tentatives. L'équipe rédige la formule chiffrée (poids, seuils) avant #11 ; Ange la valide. Pas de date : validation écrite requise.

## À confirmer au passage (non bloquant)
- Le texte de la PR #14 présente l'indice (tuteur V2) comme la « seule voie » par laquelle la solution atteint l'étudiant, plus strict que `CLAUDE.md`. Sans objection d'Ange le 2026-10-25, l'équipe adoucit la formulation dans une prochaine PR.

## Traité
- [x] 2026-10-23 : Q2 (courbe de niveaux) validée par Ange ; Q5 : option A retenue (issue du type I à rédiger en `a-cadrer`) ; Q4 : principe de maîtrise donné, formule à rédiger. Voir `state/decisions.md`.
- [x] Blacklist JWT (#5) : tranchée par l'équipe le 2026-10-20 (réglage de sécurité), activée, `ready` posé. Voir `state/decisions.md`.
- [x] Création de PR en mode headless : la PR #14 a été créée, donc `gh pr create` et `git push` fonctionnent. En revanche `gh pr ready` est refusé (approbation requise) : voir le plan.
- [x] Typecheck frontend cassé : issue #15 créée, `ready`.
- [x] Épingler ruff : issue #16 créée, `ready`.
- [x] PR #12 mergée (issue #1).
- [x] Questions techniques d'avant l'autonomie : traitées ci-dessus.
