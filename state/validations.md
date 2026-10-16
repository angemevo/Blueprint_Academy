# File de validation d'Ange

Coche la case, ou écris ta réponse sous le point. L'orchestrateur lit ce fichier au début de chaque cycle de pilotage.

## En attente

### Bloquant : à traiter en premier
- [ ] **Rendre GitHub accessible aux cycles headless.** Le 2026-10-16, le pilotage n'a pas pu lire les issues ni les PR : `gh` a été refusé parce que l'espace de travail n'est pas approuvé, et les 46 autorisations de `.claude/settings.json` ont été ignorées (`logs/2026-10-16_1114-pilotage.json`). Recommandation : lancer `claude` une fois en interactif dans `/home/gael/Blueprint_Academy` et accepter la boîte d'approbation de l'espace de travail, puis relancer `scripts/cycle.sh pilotage`.
- [ ] **Confirmer les numéros GitHub des issues.** Le plan cite des numéros présumés (#1 à #11, dans l'ordre des fichiers `issues/01` à `issues/11`). Recommandation : vérifier avec `gh issue list` que `scripts/creer-issues.sh` n'a tourné qu'une fois et que les numéros correspondent, sinon noter ici les vrais numéros.
- [ ] **Poser `ready`** sur « Outillage qualité » (présumée #1) et « Interfaces de validation » (présumée #2). Recommandation : oui pour les deux, aucune décision de fond en jeu ; ce sont les deux premières du prochain plan.

### Décisions sur des issues
- [ ] Issue « Authentification JWT » (présumée #5) : activer `token_blacklist` et `BLACKLIST_AFTER_ROTATION` ? Recommandation : oui, puis poser `ready`. Elle ouvre la chaîne API, qui est le chemin critique vers la soumission.
- [ ] Issue « Validateurs A, B, C, D » (présumée #3) : valider la règle de score proposée (A et B tout ou rien, C et D au prorata, correct seulement à 100). Recommandation : accepter, puis poser `ready` une fois les interfaces (#2) mergées.
- [ ] Issue « XP et niveaux » (présumée #10) : valider le principe d'un réglage `XP_LEVEL_THRESHOLDS`. Recommandation : oui, avec des valeurs initiales à fixer d'ici à ce que la soumission (#9) soit mergée.

### Issues `a-cadrer` (jamais confiées aux agents avant ton cadrage)
- [ ] Issue « Moteur de validation de graphe (E, F, G, H) » (présumée #4) : répondre aux 5 questions et écrire les cas de test à partir de vrais Blueprints vérifiés dans Unreal. Recommandation : commencer maintenant, car c'est le cœur pédagogique et le délai le plus long de la phase 2b.
- [ ] Issue « Calcul de la maîtrise des skills » (présumée #11) : fixer la formule, le bonus du type I, le seuil du contrôle d'intégrité et les réglages. Recommandation : à traiter après le moteur de graphe, elle n'est utile qu'une fois la soumission (#9) livrée.
- [ ] Type I (normalisation de l'export UE5 en graphe) : aucune issue n'existe alors que le type I fait partie du P0, et `issues/04` le renvoie à une « issue séparée ». Recommandation : rédiger cette issue en `a-cadrer` après le cadrage du moteur de graphe, dont elle dépend.

### PR prêtes à merger
- [ ] Impossible de lister les PR ouvertes ce cycle (accès `gh` refusé). Recommandation : aucune PR d'agent n'est attendue puisqu'aucune issue n'était `ready` ; vérifier quand même avec `gh pr list`.

## Traité
