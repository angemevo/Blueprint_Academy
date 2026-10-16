# File de validation d'Ange

Coche la case, ou écris ta réponse sous le point. L'orchestrateur lit ce fichier au début de chaque cycle de pilotage.

## En attente

### Bloquant : à traiter en premier
- [ ] **Poser `ready` sur les deux premières issues.** Aucune issue n'est `ready`, donc le plan reste vide. Recommandation : #2 (interfaces de validation) et #5 (auth JWT, après la décision blacklist ci-dessous), car #5 ouvre la chaîne API, le chemin critique (5 issues en série jusqu'à la soumission #9). Repli si tu ne tranches pas la blacklist tout de suite : #1 (outillage qualité) et #2.
- [ ] **Commandes `gh` composées refusées en mode headless.** Ce cycle, les commandes `gh` simples passent, mais trois commandes ont été refusées automatiquement : une boucle `for`, un enchaînement avec `gh label list`, et une commande contenant du texte entre guillemets avec `$(...)`. Risque : le cycle tech pourrait être bloqué au moment d'ouvrir une PR (`gh pr create --title "..." --body "..."`). Recommandation : vérifier avant le premier cycle tech utile qu'une création de PR passe en headless (par exemple avec `--body-file`), sinon ajuster les autorisations.

### Décisions sur des issues
- [ ] #5 Authentification JWT : activer `token_blacklist` et `BLACKLIST_AFTER_ROTATION` ? Recommandation : oui, pour qu'un refresh volé ou déconnecté ne soit plus réutilisable ; puis poser `ready`.
- [ ] #3 Validateurs A, B, C, D : valider la règle de score proposée (A et B tout ou rien, C et D au prorata, correct seulement à 100). Recommandation : accepter, puis poser `ready` une fois #2 mergée.
- [ ] #10 XP et niveaux : valider le principe d'un réglage `XP_LEVEL_THRESHOLDS`. Recommandation : oui, valeurs initiales à fixer avant que #9 soit mergée.

### Issues `a-cadrer` (jamais confiées aux agents avant ton cadrage)
- [ ] #4 Moteur de validation de graphe (E, F, G, H) : répondre aux 5 questions et écrire les cas de test à partir de vrais Blueprints vérifiés dans Unreal. Recommandation : commencer maintenant, c'est le cœur pédagogique et le délai le plus long de la phase 2b.
- [ ] #11 Calcul de la maîtrise des skills : fixer la formule, le bonus du type I, le seuil du contrôle d'intégrité et les réglages. Recommandation : après #4 ; elle n'est utile qu'une fois #9 livrée.
- [ ] Type I (normalisation de l'export UE5 en graphe) : aucune issue n'existe alors que le type I fait partie du P0 et que #4 le renvoie à une « issue séparée ». Recommandation : rédiger cette issue en `a-cadrer` après le cadrage de #4, dont elle dépend.

### PR prêtes à merger
- Aucune PR ouverte (vérifié avec `gh pr list` le 2026-10-16).

## Traité
- [x] Rendre GitHub accessible aux cycles headless : constaté par le pilotage du 2026-10-16 (2e cycle), `gh issue list`, `gh issue view` et `gh pr list` fonctionnent. Reste le point sur les commandes composées, ci-dessus.
- [x] Confirmer les numéros GitHub des issues : constaté le 2026-10-16, #1 à #11 correspondent aux fichiers `issues/01` à `issues/11` (titres identiques, une seule exécution de `scripts/creer-issues.sh`).
