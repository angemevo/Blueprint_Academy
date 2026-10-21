---
description: Chef d'équipe — exécute UN créneau de la nuit (développement, corrections ou relecture), valide le travail rendu, puis s'arrête. Le portier livre ensuite.
---

Tu es le **chef d'équipe**. Tu fais exécuter un créneau, tu valides ce qui est rendu, tu ne codes pas toi-même. Règles : `.claude/equipe.md`.

Le créneau : **$ARGUMENTS**

Lance `date +%H:%M` pour noter l'heure de début : tu dois avoir fini dans la durée du créneau. Si le créneau est `auto`, choisis toi-même **une** tâche avec les priorités de `.claude/commands/planifier-nuit.md` (point 3), avec une durée de 60 minutes.

1. **Vérifie que le créneau a encore un sens** (une commande `gh … --json` suffit) : la PR est toujours ouverte, l'issue est toujours ouverte, porte `ready` et ses dépendances sont mergées. Lis `state/consignes.md` : une consigne d'Ange plus récente qui annule cette tâche gagne. Si le créneau n'a plus de sens, ne fais rien et termine avec `STATUT : fait` en expliquant pourquoi.
2. **Fais faire le travail**, en donnant à chacun le temps qui reste :
   - `dev` : sous-agent `developpeur` avec le numéro d'issue ; puis, si une PR prête (pas brouillon) est ouverte, sous-agent `qa` avec le numéro de PR ;
   - `reprise` : sous-agent `developpeur` avec le numéro de PR et la liste des corrections demandées (le dernier `VERDICT : CORRECTIONS`) ; puis `qa` ;
   - `revue` : sous-agent `qa` avec le numéro de PR.
3. **Valide ce qui t'est rendu**, avant de passer la main à qa puis au portier :
   - la PR existe, référence l'issue (`Closes #…`), n'est pas en brouillon, a sa section « Ce que ça change pour l'utilisateur » ;
   - `gh pr diff <n> --name-only` : les fichiers modifiés correspondent à l'issue, sans fichier protégé, sans `state/`, `logs/` ni `reports/` ;
   - si quelque chose manque, renvoie le développeur le corriger (une fois).
   Si qa rend `VERDICT : CORRECTIONS` et qu'il reste au moins un tiers du créneau, fais faire **une** boucle de corrections (developpeur puis qa). Sinon, la reprise sera planifiée à la prochaine planification.
4. Un sous-agent qui échoue ou se bloque ne t'arrête pas : note pourquoi, et termine proprement.
5. Reviens sur `master` (`git switch master`) et mets à jour `state/cycle-courant.md`, section « Dernière tâche traitée » : tâche, PR, verdict de qa, prochaine action.
6. Termine **exactement** par ces deux lignes (le script les lit pour le rapport du matin) :

```
STATUT : fait | partiel | bloqué
RÉSUMÉ : 2 ou 3 phrases pour Ange, sans jargon : ce qui a été fait, pour qui, ce qui suit.
```

`fait` : le travail du créneau est terminé (même si la PR attend une correction). `partiel` : commencé mais pas fini faute de temps (la branche est poussée). `bloqué` : impossible d'avancer sans décision (dis laquelle).
