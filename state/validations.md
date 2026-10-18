# File de validation d'Ange

Coche la case, ou écris ta réponse sous le point. L'orchestrateur lit ce fichier au début de chaque cycle de pilotage.

Mise à jour : pilotage du 2026-10-16 (3e cycle).

## En attente

### Bloquant pour la semaine prochaine (S43) : à traiter en premier
- [ ] **#5 Authentification JWT : activer `token_blacklist` et `BLACKLIST_AFTER_ROTATION` ?** Sans ta réponse, #5 ne peut pas être `ready`. Or c'est la tête du chemin critique (#5 → #6 → #7 → #8 → #9), et chaque semaine de retard repousse la soumission d'autant. Recommandation : oui, pour qu'un refresh volé ou déconnecté ne soit plus réutilisable. Écris la décision en commentaire de l'issue, puis pose `ready`.
- [ ] **Création de PR en mode headless à vérifier.** Le cycle tech va ouvrir sa première PR (#1). Des commandes composées ou avec `$(...)` ont déjà été refusées. Ce cycle-ci, `git -C <dossier> show` a aussi été refusé (approbation requise). Recommandation : vérifier que `gh pr create --title ... --body-file <fichier>` et les commandes `git` utiles au cycle tech (`git switch -c`, `git add <fichier>`, `git commit`, `git push`) sont autorisées dans `.claude/settings.json`, avant le prochain cycle tech.

### Décisions sur des issues
- [ ] #3 Validateurs A, B, C, D : valider la règle de score proposée (A et B tout ou rien, C et D au prorata, correct seulement à 100). Recommandation : accepter, puis poser `ready` dès que #2 est mergée, pour la mettre au plan S43.
- [ ] #10 XP et niveaux : valider le principe d'un réglage `XP_LEVEL_THRESHOLDS`. Recommandation : oui, avec des valeurs initiales à fixer avant que #9 soit mergée (vers S47).

### Issues `a-cadrer` (jamais confiées aux agents avant ton cadrage)
- [ ] #4 Moteur de validation de graphe (E, F, G, H) : répondre aux 5 questions et écrire les cas de test à partir de vrais Blueprints vérifiés dans Unreal. Recommandation : commencer maintenant. C'est le cœur pédagogique et le délai le plus long de la phase 2b. Des places restent libres dans le plan de S44 à S46.
- [ ] #11 Calcul de la maîtrise des skills : fixer la formule, le bonus du type I, le seuil du contrôle d'intégrité et les réglages. Recommandation : après #4. Elle ne sert qu'une fois #9 livrée.
- [ ] Type I (normalisation de l'export UE5 en graphe) : aucune issue n'existe, alors que le type I fait partie du P0 et que #4 le renvoie à une « issue séparée ». Recommandation : rédiger cette issue en `a-cadrer` après le cadrage de #4, dont elle dépend.

### PR prêtes à merger
- [ ] **PR #14 prête à merger** (issue #2, interfaces de validation et registre). Revue qualité du 2026-10-18, verdict OK : pytest (78 passed), ruff, makemigrations --check et lint passent. L'échec du typecheck est identique sur `master`, donc hors périmètre. La PR est encore en brouillon : `gh pr ready 14`, puis merger. Points de design à confirmer : la signature de `HintService.next_hint(exercise, submission, result, hints_used) -> str | None`, `feedback` / `hints` typés `list[str]`, et le docstring de `HintService` qui fait de l'indice la « seule voie » par laquelle la solution atteint le client (plus strict que CLAUDE.md).
- [ ] **Typecheck frontend cassé sur `master`** (constaté le 2026-10-18). `frontend/tsconfig.json` inclut `.next/dev/types/**/*.ts`, que `next dev` régénère. Avec `noUnusedLocals` / `noUnusedParameters`, ce fichier donne TS6196 et TS6133. Tant que ce n'est pas corrigé, aucune PR ne passe la vérification obligatoire. Recommandation : ouvrir une issue d'outillage `ready`, par exemple pour sortir `.next/dev/types` de l'`include`.
- [ ] **PR #13 « Sécurité : mise à jour de Next.js (npm audit fix) »** : ouverte le 2026-10-18, sans revue qa. Elle sera relue au prochain cycle tech, si tu le souhaites.

## Traité
- [x] PR #12 mergée (issue #1, outillage qualité), constaté le 2026-10-18. Restent à faire : lancer `npm audit` (la PR #13 semble s'en charger) et ouvrir une issue pour épingler ruff sur une version mineure.
- [x] Poser `ready` sur deux issues : constaté le 2026-10-16 (pilotage, 3e cycle). `ready` est posé sur #1 et #2, ce qui correspond au repli recommandé. Les deux sont au plan S42.
- [x] Retirer `ready` de #10 et #11 : constaté le 2026-10-16 (pilotage, 3e cycle). Seules #1 et #2 portent `ready`.
- [x] Rendre GitHub accessible aux cycles headless : constaté par le pilotage du 2026-10-16 (2e cycle). `gh issue list`, `gh issue view` et `gh pr list` fonctionnent. Reste le point sur la création de PR, ci-dessus.
- [x] Confirmer les numéros GitHub des issues : constaté le 2026-10-16. #1 à #11 correspondent aux fichiers `issues/01` à `issues/11` (titres identiques, une seule exécution de `scripts/creer-issues.sh`).
