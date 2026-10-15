---
description: Cycle tech — traite UNE issue (développement puis revue qualité) et s'arrête.
---

Tu pilotes un cycle tech. Tu délègues, tu ne codes pas toi-même.

1. Lis `state/cycle-courant.md`.
2. Choisis UNE seule tâche, dans cet ordre de priorité :
   a. une PR dont le dernier verdict qa est `VERDICT : CORRECTIONS` → confie-la au sous-agent `developpeur` avec le numéro de PR et la liste des corrections ;
   b. sinon, la première issue du plan de la semaine encore non traitée, à condition qu'elle porte l'étiquette `ready` (`gh issue view <n> --json labels`) → confie-la au sous-agent `developpeur` ;
   c. sinon, rien à faire : écris « Plan de la semaine terminé » dans `state/cycle-courant.md` et arrête-toi.
3. Quand le `developpeur` a ouvert ou mis à jour une PR, confie-la au sous-agent `qa`.
4. Ne relance pas une deuxième boucle développement → qa dans ce cycle : les corrections éventuelles seront traitées au prochain cycle.
5. Avant de terminer, vérifie que tu es revenu sur `master` (`git switch master`), puis mets à jour :
   - `state/cycle-courant.md` : tâche traitée, numéro de PR, verdict qa, prochaine action ;
   - `state/quota.md` : ajoute une ligne `| AAAA-MM-JJ | cycle-tech | <issue ou PR> | terminé / bloqué |`.
6. Termine par un résumé de 5 lignes maximum.

Si la session devient longue, écris d'abord l'état dans `state/cycle-courant.md`, puis continue : en cas de coupure par la limite d'usage, le prochain cycle reprendra là.
