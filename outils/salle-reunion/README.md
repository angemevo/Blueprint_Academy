# Salle de réunion des agents

Une interface locale pour suivre l'équipe d'agents comme une réunion : chaque agent rejoint la salle quand on lui confie une tâche et la quitte quand il a fini.

```bash
scripts/salle-reunion.sh          # ouvre http://127.0.0.1:8765
```

Puis clique sur **Son coupé** pour activer les sons et la voix (le navigateur l'exige). Pour voir le rendu sans attendre un cycle, clique sur **Démo**.

## Ce que montre l'écran

| Zone | Contenu |
| --- | --- |
| Tuiles | Les agents présents. L'anneau violet signale celui qui parle ; la ligne du haut dit ce qu'il fait. |
| Terminaux | Un onglet par agent : commandes lancées, fichiers lus ou modifiés, sorties. Clique sur un onglet pour l'épingler. |
| Conversation | Ce que les agents se disent, les consignes données à chaque agent, leurs comptes rendus, le bilan final. |
| Journal | Tous les événements horodatés : entrées, sorties, outils, erreurs, refus d'autorisation. |

## Trois façons de regarder

- **Direct** (par défaut) : suit le cycle en cours et bascule tout seul sur le suivant. Si tu ouvres la page au milieu d'un cycle, elle rattrape ce qui s'est déjà passé en silence, puis parle à nouveau.
- **Revoir un cycle** : rejoue un cycle passé, par exemple celui que cron a lancé pendant la nuit, avec la voix. Vitesse ×1, ×2 ou ×4.
- **Démo** : une réunion d'exemple (une issue développée puis relue).

## Fonctionnement

`scripts/cycle.sh` enregistre chaque cycle dans `logs/<date>-<cycle>.jsonl` (format `stream-json` de Claude Code). `serveur.py` lit ces fichiers et les transmet à la page. Il n'utilise que Python, sans dépendance. Il n'écoute que sur ta machine (127.0.0.1) et ne consomme ni quota Claude ni données mobiles.

La voix est celle de ton navigateur (synthèse vocale). Sous Ubuntu, Chrome et Firefox proposent en général une voix française. Si aucune n'est installée, les sons de connexion restent actifs.
