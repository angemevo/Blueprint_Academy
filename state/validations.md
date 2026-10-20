# Questions pour Ange

Tenu par l'orchestrateur. Seules les questions qui reviennent à Ange y figurent (voir « Qui décide quoi » dans `.claude/equipe.md`), chacune avec options, recommandation et date. Elles sont recopiées dans le point hebdo du dimanche, où Ange répond en commentaire.

Mise à jour : pilotage du 2026-10-20 (semaine 2026-S43). Aucune réponse d'Ange trouvée : aucun point hebdo n'avait encore été publié.

## En attente

- [ ] **Q1 — Règle de score des exercices de rappel et de transition (#3).** Contexte : A et B tout ou rien ; C (ordre) et D (paires) au prorata des éléments justes ; « réussi » seulement à 100. Options : A : accepter ; B : tout ou rien aussi pour C et D. Recommandation : A, parce qu'un score partiel motive sans valider à tort. Sans réponse le 2026-10-25 : A appliquée, `ready` posé sur #3 dès que #2 est mergée.
- [ ] **Q2 — Courbe de niveaux (#10).** Contexte : les niveaux se règlent par une liste de seuils d'XP dans les réglages, modifiable sans toucher au code. Options : A : accepter le principe ; B : niveaux à pas fixe. Recommandation : A, valeurs de départ proposées par l'équipe avant la livraison de #9 (vers S47). Sans réponse le 2026-10-25 : A appliquée.
- [ ] **Q3 — Cadrage du moteur de validation de graphe (#4).** Contexte : la proposition de l'équipe est en commentaire de l'issue #4 (score = part des exigences, interdits = jamais « réussi », node verrouillé supprimé = refus). Les cas de test doivent être vérifiés dans Unreal. Options : A : valider ce cadrage, puis fournir des exports de vrais Blueprints ; B : le modifier. Recommandation : A. Pas d'application par défaut (vérification Unreal) : #4 reste `a-cadrer` sans réponse. Date de relance : 2026-10-25.
- [ ] **Q4 — Calcul de la maîtrise (#11).** Contexte : formule, bonus du type I, seuil du contrôle de contenu, à fixer avant #11, qui ne sert qu'après #9 (vers S47). Options : A : l'équipe rédige une proposition après #4 ; B : tu la rédiges. Recommandation : A. Sans réponse le 2026-10-25 : A appliquée (proposition rédigée, validation d'Ange toujours requise).
- [ ] **Q5 — Issue pour le type I (export Unreal en graphe).** Contexte : le type I fait partie du MVP mais aucune issue n'existe. Options : A : l'équipe rédige l'issue en `a-cadrer` après le cadrage de #4 ; B : on la reporte après le MVP. Recommandation : A. Sans réponse le 2026-10-25 : A appliquée.

## À confirmer au passage (non bloquant)
- Le texte de la PR #14 présente l'indice (tuteur V2) comme la « seule voie » par laquelle la solution atteint l'étudiant, plus strict que `CLAUDE.md`. Sans objection d'Ange le 2026-10-25, l'équipe adoucit la formulation dans une prochaine PR.

## Traité
- [x] Blacklist JWT (#5) : tranchée par l'équipe le 2026-10-20 (réglage de sécurité), activée, `ready` posé. Voir `state/decisions.md`.
- [x] Création de PR en mode headless : la PR #14 a été créée, donc `gh pr create` et `git push` fonctionnent. En revanche `gh pr ready` est refusé (approbation requise) : voir le plan.
- [x] Typecheck frontend cassé : issue #15 créée, `ready`.
- [x] Épingler ruff : issue #16 créée, `ready`.
- [x] PR #12 mergée (issue #1).
- [x] Questions techniques d'avant l'autonomie : traitées ci-dessus.
