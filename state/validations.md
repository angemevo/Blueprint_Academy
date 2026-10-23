# Questions pour Ange

Tenu par l'organisateur. Seules les questions qui reviennent à Ange y figurent (voir « Qui décide quoi » dans `.claude/equipe.md`), chacune avec options, recommandation et date. Elles sont posées à Ange dans son bureau (rapport du dimanche et rapport du matin), où il répond en commentaire.

Mise à jour : pilotage du 2026-10-20 (semaine 2026-S43). Aucune réponse d'Ange trouvée : aucun point hebdo n'avait encore été publié.

## En attente

- [ ] **Q6 — Passer à la phase 3 (écrans du site) ?** Contexte : toute la partie serveur de la phase 2 est livrée (connexion, catalogue, exercices, correction des rappels, soumission, points et niveaux, progression, tableau de bord). Il ne reste que trois lots qui attendent Ange (correction des graphes #4 après les exports Unreal du 24 octobre, maîtrise #11, lecture d'un export Unreal). Options : A : démarrer la phase 3 maintenant (socle du site, connexion, vitrine) pendant que les lots en attente se débloquent ; B : attendre la fin complète de la phase 2. Recommandation : A, parce que l'équipe n'a plus rien de prêt et que la phase 3 produit des écrans qu'Ange pourra voir. Sans réponse le 2026-11-01 : A appliquée par défaut.
- [ ] **Q7 — Formule de maîtrise (#11).** Une proposition chiffrée est en commentaire de l'issue #11 (voir Q4bis). Ange la valide ou la corrige.
- [ ] **Q4bis — Formule de maîtrise (#11).** Principe reçu d'Ange : maîtrise = réussir sans erreur, plus vite que la moyenne, avec le moins de tentatives. L'équipe rédige la formule chiffrée (poids, seuils) avant #11 ; Ange la valide. Pas de date : validation écrite requise.

## À confirmer au passage (non bloquant)
- Le texte de la PR #14 présente l'indice (tuteur V2) comme la « seule voie » par laquelle la solution atteint l'étudiant, plus strict que `CLAUDE.md`. Sans objection d'Ange le 2026-10-25, l'équipe adoucit la formulation dans une prochaine PR.

## Traité
- [x] 2026-10-23 : Q3 (cadrage du moteur de validation, #4) : Ange suit la recommandation, option A, cadrage validé. #4 reste `a-cadrer` jusqu'aux exports Unreal du samedi 24 octobre (cas de test à vérifier dans Unreal).
- [x] 2026-10-23 : Q1 (score des exercices de rappel et de transition) : Ange répond A (score partiel pour l'ordre et les paires). `ready` posé sur #3.
- [x] 2026-10-23 : Q2 (courbe de niveaux) validée par Ange ; Q5 : option A retenue (issue du type I à rédiger en `a-cadrer`) ; Q4 : principe de maîtrise donné, formule à rédiger. Voir `state/decisions.md`.
- [x] Blacklist JWT (#5) : tranchée par l'équipe le 2026-10-20 (réglage de sécurité), activée, `ready` posé. Voir `state/decisions.md`.
- [x] Création de PR en mode headless : la PR #14 a été créée, donc `gh pr create` et `git push` fonctionnent. En revanche `gh pr ready` est refusé (approbation requise) : voir le plan.
- [x] Typecheck frontend cassé : issue #15 créée, `ready`.
- [x] Épingler ruff : issue #16 créée, `ready`.
- [x] PR #12 mergée (issue #1).
- [x] Questions techniques d'avant l'autonomie : traitées ci-dessus.
