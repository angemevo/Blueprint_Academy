Titre: Outillage qualité : ruff (backend) et ESLint (frontend)
Labels: phase-2b,outillage
---
**Dépend de :** aucune

## Pourquoi
Les agents et la CI ont besoin d'un lint automatique pour garder le code homogène sans revue manuelle de style.

## Ce qui est attendu
- Backend : ajouter `ruff` à `requirements-dev.txt` (cette issue autorise explicitement la modification de ce fichier) et une configuration `backend/ruff.toml` : règles `E`, `F`, `I`, `UP`, `B`, cible Python 3.12.
- Corriger les violations existantes **sans changer le comportement**. Si une règle impose une réécriture risquée, l'ignorer dans `ruff.toml` avec un commentaire qui explique pourquoi.
- Frontend : ESLint en configuration plate `frontend/eslint.config.mjs` avec la configuration Next.js et TypeScript, et un script `"lint"` dans `package.json` (cette issue autorise explicitement sa modification et celle du lockfile). Le lockfile doit être régénéré **dans le conteneur** (`docker compose exec -T frontend npm install --package-lock-only`), pour garder les binaires Alpine.

## Critères d'acceptation
- [ ] `ruff check .` passe dans `backend/`.
- [ ] `npm run lint` passe dans `frontend/`.
- [ ] `pytest` et `npm run typecheck` passent toujours.
- [ ] Aucun changement de logique dans le diff hors corrections de lint triviales (imports, annotations).

## Hors périmètre
- `ruff format` ou Prettier sur tout le code (reformatage massif).
- Toute modification de `.github/`.
