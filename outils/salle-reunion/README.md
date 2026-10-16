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

## Voix naturelles (recommandé)

Sous Ubuntu, la voix du navigateur est souvent eSpeak, très robotique. Pour des voix humaines, installe **Piper**, une synthèse vocale neuronale qui tourne entièrement sur ta machine :

```bash
sudo apt install -y python3-venv     # si ce n'est pas déjà fait
scripts/installer-voix.sh            # 2 voix : Jessica et Pierre, environ 140 Mo à télécharger
scripts/installer-voix.sh --complet  # 4 voix : + Siwis et Tom, environ 270 Mo
```

C'est un téléchargement unique, à faire de préférence avec un bon signal. Ensuite, tout fonctionne hors connexion. Le script génère un exemple par agent dans `outils/salle-reunion/test-voix/` : écoute-les avec `aplay`.

Relance ensuite `scripts/salle-reunion.sh` et choisis **Voix naturelles (Piper)** dans la liste des voix (choix par défaut quand Piper est installé).

| Agent | Voix (installation de base) | Voix (installation complète) |
| --- | --- | --- |
| Pilote du cycle | Jessica | Siwis |
| Orchestrateur | Pierre, plus posé | Tom |
| Développeur | Pierre, plus vif | Pierre |
| QA | Jessica, plus posée | Jessica |

Sans Piper, la liste propose les voix françaises du navigateur, les plus naturelles en tête (sous Chrome, « Google français » est nettement meilleure qu'eSpeak, mais elle passe par Internet).
