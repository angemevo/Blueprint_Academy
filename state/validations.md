# Questions pour Ange

Tenu par l'organisateur. Seules les questions qui reviennent à Ange y figurent (voir « Qui décide quoi » dans `.claude/equipe.md`), chacune avec options, recommandation et date. Elles sont posées à Ange dans son bureau (rapport du dimanche et rapport du matin), où il répond en commentaire.

Mise à jour : pilotage du 2026-11-08 (semaine 2026-S45).

## En attente
- **Q1** : retirer le type I (import Unreal) du MVP dans `CLAUDE.md` (fichier protégé, seul Ange le modifie). Contexte : la consigne du 2026-10-25 est appliquée par l'équipe. Options : A (Ange modifie le document, type I en V3) / B (document inchangé, l'équipe suit la consigne). Recommandation : A, pour que le document reflète la décision. Sans réponse le 2026-11-15 : B (déjà appliquée dans les faits).
- **Q2** : lancer dès maintenant la phase 6 (tests de bout en bout du parcours étudiant), en parallèle de la phase 5 ? Contexte : la phase 5 avance en propositions et attendra tes validations ; l'équipe aurait sinon peu à faire. Options : A (oui, phase 6 en parallèle) / B (non, une phase à la fois). Recommandation : A, les tests ne dépendent pas du contenu. Sans réponse le 2026-11-15 : A.

## Traité
- [x] 2026-11-08 : Q3 (phase 5) : sans réponse à l'échéance, option A appliquée par défaut. Issues #66 et #67 `ready`.
- [x] 2026-11-08 : Q2 (contenu du parcours de départ) : sans réponse à l'échéance, option A appliquée par défaut (propositions, rien publié sans Ange).
- [x] 2026-11-01 : Q3bis (phase 4, admin) : sans réponse à l'échéance, option A appliquée par défaut. Issues #61 et #62 `ready`.
- [x] 2026-11-01 : ancienne Q2 (adoucir la PR #14, déjà mergée) : option A appliquée par défaut, sans objet.
- [x] 2026-10-25 : Q6 (phase 3) : Ange répond oui. Issues #31 à #34 `ready`.
- [x] 2026-10-25 : Q7 / Q4bis (formule de maîtrise) : validée par Ange. #11 `ready`.
- [x] 2026-10-23 : Q3 (cadrage du moteur de validation, #4) : Ange suit la recommandation, option A, cadrage validé. #4 reste `a-cadrer` jusqu'aux exports Unreal du samedi 24 octobre (cas de test à vérifier dans Unreal).
- [x] 2026-10-23 : Q1 (score des exercices de rappel et de transition) : Ange répond A (score partiel pour l'ordre et les paires). `ready` posé sur #3.
- [x] 2026-10-23 : Q2 (courbe de niveaux) validée par Ange ; Q5 : option A retenue (issue du type I à rédiger en `a-cadrer`) ; Q4 : principe de maîtrise donné, formule à rédiger. Voir `state/decisions.md`.
- [x] Blacklist JWT (#5) : tranchée par l'équipe le 2026-10-20 (réglage de sécurité), activée, `ready` posé. Voir `state/decisions.md`.
- [x] Création de PR en mode headless : la PR #14 a été créée, donc `gh pr create` et `git push` fonctionnent. En revanche `gh pr ready` est refusé (approbation requise) : voir le plan.
- [x] Typecheck frontend cassé : issue #15 créée, `ready`.
- [x] Épingler ruff : issue #16 créée, `ready`.
- [x] PR #12 mergée (issue #1).
- [x] Questions techniques d'avant l'autonomie : traitées ci-dessus.

## Ajout du 2026-11-09 (réapprovisionnement)
- **Q3** : relire le premier module proposé (leçons et exercices, non publiés) et le valider ? Contexte : les propositions sont dans la base de démarrage, rien n'est visible des étudiants ; les points qui touchent à Unreal sont marqués « à vérifier dans Unreal ». Options : A (tu relis et tu valides ou corriges) / B (autre ordre : on passe d'abord aux tests). Recommandation : A, car les modules suivants en dépendent. Pas d'application par défaut : le contenu ne se publie jamais sans ton accord.
