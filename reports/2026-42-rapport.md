# Rapport hebdo : 2026, semaine 42

Mis à jour au 2e cycle de pilotage du 2026-10-16. Phase en cours : 2b (services, validateurs et API), MVP / P0.

## Livré
- Code : rien. Aucune issue n'était `ready`, aucune PR n'a été ouverte.
- Organisation : l'accès GitHub en mode headless fonctionne pour les commandes simples. Les numéros des issues sont confirmés (#1 à #11).

## Bloqué
- **Aucune issue `ready`** sur GitHub, donc le plan de la semaine est vide.
- Candidates sans dépendance : #2 (interfaces de validation), #5 (auth JWT, décision blacklist à prendre) et #1 (outillage qualité).
- Deux issues `a-cadrer` attendent ton cadrage : #4 (moteur de graphe) et #11 (maîtrise). L'issue du type I n'existe pas encore.
- Risque : des commandes `gh` composées ou avec guillemets ont été refusées en headless. La création de PR par le cycle tech reste à vérifier.

## Quota
- Semaine précédente : aucun cycle, aucun cycle coupé. La limite de 2 issues par semaine s'applique.
- Cette semaine : 2 cycles terminés (pilotage, tech) avant celui-ci, aucun coupé.

## Point d'attention prioritaire
Poser `ready` sur #2 et #5 après avoir tranché la blacklist JWT (recommandation : oui). #5 ouvre la chaîne API (#5 → #6 → #7 → #8 → #9), qui avance d'au plus une issue par semaine : chaque semaine sans démarrage repousse la soumission d'autant.

Détail des décisions à prendre : `state/validations.md`.
