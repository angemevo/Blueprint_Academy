# Règles de l'équipe d'agents

Ce fichier complète `CLAUDE.md`, qui reste la source de vérité du projet. En cas de conflit, `CLAUDE.md` gagne. En session interactive, une demande explicite d'Ange prime sur ces règles.

## Décisions verrouillées

Tout ce que `CLAUDE.md` marque « verrouillé » (principes, stack, catalogue de nodes, taxonomie, règles de validation) ne se modifie jamais dans une PR d'agent. Si une issue semble l'exiger : écris la question dans `state/validations.md` et arrête-toi.

## Vérifications obligatoires avant d'ouvrir une PR

La stack Docker doit tourner (`docker compose up -d --wait postgres backend frontend` ; le script de cycle le fait).

- Tests backend : `docker compose exec -T backend pytest`
- Migrations à jour : `docker compose exec -T backend python manage.py makemigrations --check --dry-run`
- Types frontend : `docker compose exec -T frontend npm run typecheck`
- Lint : `docker compose exec -T backend ruff check .` et `docker compose exec -T frontend npm run lint`, **une fois l'issue d'outillage qualité mergée**.

Quand une issue autorise un changement de dépendances, installe-les dans le conteneur (`docker compose exec -T backend pip install -r requirements-dev.txt`, `docker compose exec -T frontend npm install`) : jamais sur la machine hôte, pour garder les binaires Alpine du lockfile.

Une migration nouvelle est permise si l'issue la demande ; elle est créée avec `makemigrations`, jamais écrite à la main, et citée dans la PR.

## Une commande à la fois

Les autorisations de `.claude/settings.json` ne reconnaissent que des commandes simples. Une boucle (`for`, `while`), un enchaînement (`;`, `&&`, `||`) ou un tube (`|`) vers une autre commande est refusé, même si chaque morceau est autorisé seul.

- Lance chaque commande séparément : `gh issue view 1`, puis `gh issue view 2`.
- Pour filtrer une sortie, utilise les options de l'outil (`gh … --json labels --jq '…'`, `git log -5`), pas un tube.
- Tu es déjà à la racine du dépôt : pas de `git -C <chemin>`, pas de `docker compose -f <fichier>`, pas de chemin absolu vers le dépôt. Écris `git status`, `docker compose exec -T backend pytest`.
- Pour créer ou modifier un fichier, utilise les outils Write et Edit, jamais `sed -i`, `echo … >` ou `cat > …`.
- Pas de fichier dans `/tmp` : les brouillons (corps de PR, revues) vont dans `logs/`.

## Branches et PR

- Branche principale : `master`. Jamais de push, de merge ni de commit direct dessus.
- Une issue = une branche `feat/<numero>-<slug>` ou `fix/<numero>-<slug>` = une PR.
- PR petites : moins de 400 lignes modifiées hors migrations et lockfiles.
- Ajoute tes fichiers un par un (`git add <fichier>`), jamais `git add .` ni `git add -A`.
- Ne committe jamais `state/`, `reports/`, `logs/`, ni `frontend/next-env.d.ts` (modifié par le build).

## Mémoire de l'équipe

- `state/roadmap.md` : priorités (tenu par l'orchestrateur)
- `state/cycle-courant.md` : où en est le cycle ; à mettre à jour avant chaque arrêt
- `state/decisions.md` : décisions et leurs raisons
- `state/validations.md` : ce qu'Ange doit trancher
- `state/quota.md` : journal des cycles

Lis uniquement ce qui sert ta tâche. Le script de cycle committe `state/` et `reports/` sur `master` à la fin.

## Interdits absolus

- Lire, afficher ou committer `.env`, des clés ou des jetons.
- Modifier `CLAUDE.md`, `.claude/`, `.github/`, `docker-compose.yml`, les `Dockerfile` ou `requirements*.txt` / `package.json`, sauf si l'issue le demande explicitement.
- `docker compose down -v`, supprimer des volumes, vider la base.
- Dépenser de l'argent, créer des comptes, contacter des personnes.

En cas de doute : écris la question dans `state/validations.md` et arrête-toi.
