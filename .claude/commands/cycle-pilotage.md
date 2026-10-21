---
description: Pilotage du dimanche par l'organisateur — réponses d'Ange appliquées, bilan de la semaine pour le rapport PDF, estimation de fin, plan de la semaine suivante.
---

La semaine qui se termine est **$ARGUMENTS** : c'est le nom du bilan à écrire (`reports/hebdo/$ARGUMENTS.json`).

Confie ce cycle au sous-agent `organisateur`, en mode pilotage, en lui donnant ce nom de semaine, et laisse-le suivre ses instructions.

Quand il a terminé, vérifie, et corrige toi-même si besoin :

1. `reports/hebdo/$ARGUMENTS.json` existe et c'est du JSON valide (`jq . reports/hebdo/$ARGUMENTS.json`), au format décrit dans `.claude/agents/organisateur.md`. Il ne contient aucun jargon technique.
2. `state/cycle-courant.md` contient le plan de la semaine suivante, chaque issue avec son numéro.
3. `state/estimation.json` est du JSON valide et sa date `maj` est celle du jour.
4. Chaque question de `state/validations.md` a une recommandation et une date, et figure dans le bilan.
5. Ajoute dans `state/quota.md` : `| AAAA-MM-JJ | pilotage | - | terminé |`.

Termine par le contenu de `en_bref` du bilan.
