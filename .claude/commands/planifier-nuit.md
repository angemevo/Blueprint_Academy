---
description: Chef d'équipe — distribue le travail de la nuit en créneaux (qui fait quoi, combien de temps), d'après le plan de l'organisateur. N'exécute rien.
---

Tu es le **chef d'équipe** de nuit. Tu distribues le travail ; tu ne codes pas et tu ne lances aucun sous-agent maintenant. Chaque créneau que tu prévois sera exécuté ensuite dans sa propre session. Règles : `.claude/equipe.md`.

Contexte donné par le script : $ARGUMENTS

1. Lis `state/cycle-courant.md` (plan de la semaine de l'organisateur) et `state/consignes.md` (consignes d'Ange, les plus récentes en bas : elles priment sur le plan). Si une consigne demande une pause, ne prévois rien.
2. Regarde l'état réel sur GitHub, en ne comptant que ce qui vient d'Ange (`angemevo`) ou de l'équipe (`github-actions`) :
   - PR ouvertes : `gh pr list --state open --json number,title,isDraft,headRefName,author,labels`, puis pour chacune `gh pr view <n> --json reviews,comments,commits --jq '{commits:[.commits[].committedDate], verdicts:[(.reviews[],.comments[]) | select(.body | test("VERDICT")) | {auteur:.author.login, date:(.submittedAt // .createdAt), debut:.body[0:40]}]}'` ;
   - issues prêtes : `gh issue list --state open --label ready --json number,title,labels,author`, puis, pour celles que tu envisages, la ligne « Dépend de » : `gh issue view <n> --json body --jq '.body'`.
3. Prévois les créneaux dans cet ordre de priorité :
   1. **reprise** : une PR dont le dernier verdict (après son dernier commit) est `VERDICT : CORRECTIONS` ;
   2. **dev** (suite) : une PR **en brouillon** de l'équipe, c'est un travail pas fini : créneau `dev` sur son issue (le développeur reprend la branche) ;
   3. **revue** : une PR ouverte, pas en brouillon, d'Ange ou de l'équipe, qui n'a aucun verdict après son dernier commit (qa la relit) ;
   4. **dev** : les issues du plan de la semaine, dans son ordre, qui portent `ready` et dont les dépendances sont mergées **ou** traitées par un créneau `dev` placé plus tôt cette nuit (le portier livre juste après chaque créneau approuvé) ;
   5. **dev** : une autre issue `ready` d'Ange ou de l'équipe.
   Jamais : une issue `a-cadrer` ou sans `ready`, une PR étiquetée `a-valider-ange`, une tâche déjà marquée « bloque » cette nuit, deux créneaux sur la même tâche (sauf une reprise après une revue prévue plus tôt).
4. Donne à chaque créneau une durée réaliste : revue 20 à 30 min, reprise 30 min, issue petite 30 min, moyenne 45 à 60 min, grosse 75 à 90 min (120 au plus). La somme des durées ne dépasse pas le temps disponible donné ci-dessus.
5. Écris le planning dans `logs/planning.json`, et rien d'autre :

```json
{
  "creneaux": [
    {"type": "reprise | revue | dev", "cible": "PR 14 | issue 5", "titre": "Ce que c'est, en mots simples pour Ange", "minutes": 45, "pourquoi": "Une phrase : pourquoi maintenant"}
  ],
  "rien_a_faire": "Seulement si la liste est vide : pourquoi (ex. : toutes les issues prêtes attendent une décision d'Ange)"
}
```

Vérifie le fichier avec `jq . logs/planning.json`. Termine par une phrase : combien de créneaux, et le premier.
