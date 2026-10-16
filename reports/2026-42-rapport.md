# Rapport hebdo : 2026, semaine 42

Mis à jour au 3e cycle de pilotage du 2026-10-16. Phase en cours : 2b (services, validateurs et API), MVP / P0.

## Livré
- Code : rien pour l'instant. Aucune PR ouverte ni mergée.
- Pilotage : le plan n'est plus vide. `ready` est posé sur #1 et #2, et retiré de #10 et #11.

## Plan retenu (S42)
1. #1 Outillage qualité (ruff, ESLint). Dépend de : aucune.
2. #2 Interfaces de validation et registre. Dépend de : aucune.

## Bloqué
- #5 (auth JWT, tête du chemin critique) attend ta décision sur la blacklist et l'étiquette `ready`.
- #3 attend la validation de sa règle de score et le merge de #2.
- #4 et #11 sont `a-cadrer`. L'issue du type I n'existe pas encore.
- Risque outillage : `git -C <dossier> show` a été refusé en headless pendant ce cycle. La création de PR par le cycle tech n'a pas encore été testée.

## Quota
- Semaine précédente : aucun cycle, aucun cycle coupé. La limite de 2 issues par semaine s'applique.
- Cette semaine : 4 cycles terminés (2 de pilotage, 2 tech) avant celui-ci, aucun coupé.

## Point d'attention prioritaire
Trancher la blacklist JWT de #5 (recommandation : oui), puis poser `ready` sur #5 pour S43. #5 ouvre la chaîne API (#5 → #6 → #7 → #8 → #9), qui avance d'au plus une issue par semaine.

Détail des décisions à prendre : `state/validations.md`.
