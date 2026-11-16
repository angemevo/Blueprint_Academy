# Cycle courant

## Plan de la semaine (2026-S47, du 16 au 22 novembre) : pilotage du 2026-11-15

Q2 (phase 6 en parallèle) acceptée par défaut le 2026-11-15. Quota hebdo à 25 % : pas de limite sur le plan.

Ordre de traitement (toutes `ready`) :
1. **#71 « Tests de bout en bout : parcours étudiant par l'API (rappel) »** (backend). Dépend de : aucune ouverte.
2. **#72 « Tests de bout en bout : production, maîtrise et verrouillage »** (backend). Dépend de : #71 (outils de test).

Hors plan : #4 (`a-cadrer`, attend Ange, Q4). Modules suivants du parcours : attendent la validation du premier module (Q3). Pas de type I au MVP.
Prochains lots (pas encore d'issue) : Docker (7), documentation (8) : à écrire quand la phase 6 est mergée, avec accord pour la phase suivante.
Questions en attente d'Ange : Q3, Q4 (relance 2026-11-22).

## Réapprovisionnement 2026-11-16

#71 et #72 sont livrées (PR #74 et #75) : issues refermées, `ready` retiré, lots marqués faits. Phase 6 terminée. Plan : plus rien de prêt ; Q5 (phases 7 et 8) posée à Ange, défaut option A au 2026-11-22. Rien d'autre à planifier (Q3 et Q4 attendent Ange).

## Dernière tâche traitée

- Tâche : #72 « Tests de bout en bout : production, maîtrise et verrouillage » (créneau 3, 2026-11-15).
- PR : #75 (non brouillon, `Closes #72`, un seul fichier de test).
- Verdict de qa : APPROUVÉE. Remarque non bloquante : variable `path` et assertion `is_published` inutiles dans le test de verrouillage.
- Prochaine action : PR #75 mergée (créneau 4 : revue sans objet, aucune PR ouverte ; l'issue #72 est restée ouverte alors que la PR la ferme — à vérifier à la prochaine planification).

## Réapprovisionnement 2026-11-01

Phase 4 terminée. Aucune issue `ready` : la phase 5 attend Ange (Q3). Rien à planifier avant sa réponse ou le 2026-11-08. (Revérifié en fin de journée du 2026-11-01 : aucune réponse d'Ange, aucune issue `ready` restante ; #61 et #62 sont faites et seront refermées par leur PR.)

## Réapprovisionnement 2026-11-04

Aucune issue `ready` possible : phase 4 finie, Q3 (phase 5) sans réponse avant le 2026-11-08, #4 attend Ange. Aucun changement au plan.

## Réapprovisionnement 2026-11-05 (second passage)

Revérifié : bureau sans message d'Ange, seules #4 (`a-cadrer`) et le bureau sont ouvertes. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-05

Toujours aucune réponse d'Ange (Q1 à Q3), aucune issue `ready` possible. Aucun changement au plan ; décisions par défaut le 2026-11-08.

## Réapprovisionnement 2026-11-06

Bureau sans message d'Ange, Q1 à Q3 sans réponse (échéance 2026-11-08, pas encore passée). Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-06 (second passage)

Même constat : seules #4 (`a-cadrer`) et le bureau sont ouvertes, échéance des questions non passée. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-07

Bureau sans message d'Ange, Q1 à Q3 sans réponse (échéance 2026-11-08, pas encore passée). Aucune issue `ready` possible ; les phases 6 à 8 ne sont pas lancées sans l'accord pour la phase suivante. Plan inchangé.

## Réapprovisionnement 2026-11-07 (second passage)

Même constat : seules #4 (`a-cadrer`) et le bureau sont ouvertes, échéance des questions (2026-11-08) non passée. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-07 (troisième passage)

Bureau sans message d'Ange, aucune PR ouverte, échéance des questions (2026-11-08) non passée. Aucune issue `ready` possible. Plan inchangé ; au prochain passage après le 2026-11-08, décisions par défaut (Q3 : phase 5 en propositions).

## Réapprovisionnement 2026-11-07 (quatrième passage)

Rien de nouveau : échéance des questions (2026-11-08) non passée, aucune issue `ready` possible. Plan inchangé.

- Issue #66 : branche feat/66-seed-structure, PR ouverte, en attente de revue.

## Dernière tâche (développeur)
- Issue #67, branche feat/67-seed-module, PR #70, état : ouverte, prête pour qa.

## Réapprovisionnement 2026-11-09

#66 et #67 sont mergées (PR #69, #70) ; lots marqués faits. Aucune issue `ready` possible : modules suivants attendent la validation du premier (Q3), phase 6 attend Q2 (défaut oui au 2026-11-15), #4 reste `a-cadrer`. Plan inchangé.

## Réapprovisionnement 2026-11-09 (second passage)

Issues #66 et #67 refermées (livrées par les PR #69 et #70, l'étiquette `ready` retirée pour que l'équipe ne les reprenne pas). Aucune nouvelle issue `ready` possible : modules suivants et phase 6 attendent Ange (Q3, Q2), #4 reste `a-cadrer`. Plan inchangé.

## Réapprovisionnement 2026-11-10

Bureau sans réponse d'Ange, aucune PR ouverte, Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 toujours `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-10 (second passage)

Même constat : aucune réponse d'Ange, aucune PR ouverte, Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-11

Aucune réponse d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-11 (second passage)

Revérifié : aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible (phase 6 non lancée sans accord). Plan inchangé.

## Réapprovisionnement 2026-11-12

Aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible (phase 6 non lancée sans accord). Plan inchangé.

## Réapprovisionnement 2026-11-12 (second passage)

Revérifié : aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-13

Aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-13 (second passage)

Revérifié : aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-14

Aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15, demain) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé ; à la prochaine passe après le 2026-11-15, Q2 passe en option A par défaut et les tests de bout en bout (phase 6) pourront être écrits.

## Réapprovisionnement 2026-11-14 (second passage)

Revérifié : aucun message d'Ange, aucune PR ouverte, seules #4 (`a-cadrer`) et le bureau sont ouvertes. Q2 (échéance 2026-11-15) et Q3 sans réponse. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-14 (troisième passage)

Aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Réapprovisionnement 2026-11-14 (quatrième passage)

Aucun message d'Ange, aucune PR ouverte. Q2 (échéance 2026-11-15) et Q3 sans réponse, #4 `a-cadrer`. Aucune issue `ready` possible. Plan inchangé.

## Dernière tâche (développeur)

Issue #72, branche feat/72-e2e-production-maitrise, PR #75, état : ouverte, en attente de QA.

## Réapprovisionnement 2026-11-16 (second passage)

Aucun message d'Ange, aucune PR ouverte. Q5 (phases 7 et 8, défaut option A au 2026-11-22), Q3 et Q4 sans réponse ; #4 `a-cadrer`. Aucune issue `ready` possible (règle « attendre validation » pour la phase suivante). Plan inchangé.
