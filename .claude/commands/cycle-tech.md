---
description: Cycle tech — traite UNE tâche (développement puis revue qualité avec captures) et s'arrête. Le portier merge ensuite si tout est vert.
---

Tu pilotes un cycle tech. Tu délègues, tu ne codes pas toi-même. Règles : `.claude/equipe.md`.

1. Lis `state/cycle-courant.md`.
2. **Réponses d'Ange depuis dimanche.** Regarde le point hebdo ouvert (`gh issue list --label point-hebdo --state open --json number`) et les commentaires d'Ange seulement (`gh issue view <n> --json comments --jq '.comments[] | select(.author.login == "angemevo") | .createdAt + " " + .body'`). Pour chaque réponse plus récente que la dernière notée dans `state/cycle-courant.md` : écris la décision dans `state/decisions.md`, retire la question de `state/validations.md`, pose `ready` sur l'issue débloquée, et note la date de la réponse lue dans `state/cycle-courant.md`. Une seule fois par réponse.
3. Choisis UNE seule tâche, dans cet ordre de priorité :
   a. une PR ouverte dont le dernier verdict est `VERDICT : CORRECTIONS` et qui n'a pas reçu de commit depuis → confie-la au sous-agent `developpeur` avec le numéro de PR et la liste des corrections. Ne compte que les verdicts publiés par l'équipe (`github-actions`) ou par Ange (`angemevo`) : `gh pr view <n> --json reviews,comments,commits` ;
   b. sinon, la première issue du plan de la semaine encore non traitée, qui porte `ready` (`gh issue view <n> --json labels,state`) et dont les dépendances sont mergées → confie-la au `developpeur` ;
   c. sinon, une autre issue ouverte d'Ange ou de l'équipe qui porte `ready` et dont les dépendances sont mergées ;
   d. sinon, rien à faire : écris « Plan de la semaine terminé » dans `state/cycle-courant.md` et arrête-toi.
4. Quand le `developpeur` a ouvert ou mis à jour une PR (pas en brouillon), confie-la au sous-agent `qa`. Si la PR est en brouillon, le `developpeur` est bloqué : note le blocage et arrête-toi.
5. Ne relance pas une deuxième boucle développement → qa dans ce cycle : les corrections éventuelles seront traitées au prochain cycle. Après toi, le portier merge la PR si qa l'a approuvée et que les vérifications passent.
6. Avant de terminer, vérifie que tu es revenu sur `master` (`git switch master`), puis mets à jour :
   - `state/cycle-courant.md` : tâche traitée, numéro de PR, verdict qa, prochaine action ;
   - `state/quota.md` : ajoute une ligne `| AAAA-MM-JJ | cycle-tech | <issue ou PR> | terminé / bloqué |`.
7. Termine par un résumé de 3 lignes, compréhensible par Ange (ce qui a été fait, pour qui, ce qui suit).

Si la session devient longue, écris d'abord l'état dans `state/cycle-courant.md`, puis continue : en cas de coupure par la limite d'usage, le prochain cycle reprendra là.
