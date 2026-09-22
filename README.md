# Blueprint Academy

Plateforme web d'apprentissage **pratique** d'Unreal Engine **Blueprint**.
Philosophie : **Learn → Practice → Build → Validate → Progress**.

La source de vérité du projet (vision, stack verrouillée, architecture, modèle
de données, roadmap) est le fichier [CLAUDE.md](CLAUDE.md).

> **État : Phase 2a terminée** — architecture, configuration et modèle de
> données. La couche service, les validateurs et l'API arrivent en Phase 2b ;
> l'interface applicative en Phase 3.

## Stack

| Couche    | Technologies                                                          |
| --------- | --------------------------------------------------------------------- |
| Backend   | Python 3.12, Django 5, Django REST Framework, SimpleJWT                |
| Base      | PostgreSQL 16                                                          |
| Frontend  | Next.js 16 (App Router), TypeScript, Tailwind CSS 4, TanStack Query, Zustand |
| Infra     | Docker, `docker compose`                                               |

## Démarrage rapide

Prérequis : Docker Desktop (ou Docker Engine + plugin Compose).

```bash
cp .env.example .env     # puis ajuster DJANGO_SECRET_KEY et les mots de passe
docker compose up --build
```

Services exposés :

| Service      | URL                                  |
| ------------ | ------------------------------------ |
| Frontend     | http://localhost:3000                |
| API          | http://localhost:8000/api/           |
| Health check | http://localhost:8000/api/health/    |
| Admin Django | http://localhost:8000/admin/         |
| PostgreSQL   | `localhost:5434` (voir `POSTGRES_HOST_PORT`) |

> Le port PostgreSQL exposé sur l'hôte est configurable via
> `POSTGRES_HOST_PORT` (5434 par défaut, pour ne pas entrer en conflit avec une
> instance locale). À l'intérieur du réseau Docker, c'est toujours 5432.

Les migrations sont appliquées automatiquement au démarrage du backend
(`backend/entrypoint.sh`). Pour créer un compte d'administration :

```bash
docker compose exec backend python manage.py createsuperuser
```

## Commandes

```bash
# Développement
docker compose up --build            # démarrer les trois services
docker compose down                  # arrêter
docker compose down -v               # arrêter et supprimer les volumes (reset DB)
docker compose logs -f backend       # suivre les logs d'un service

# Django
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_blueprint   # à partir de la Phase 5

# Tests
docker compose exec backend pytest
docker compose exec frontend npm test   # à partir de la Phase 6

# Frontend
docker compose exec frontend npm run typecheck
docker compose exec frontend npm audit
```

### Après un changement de dépendances

`node_modules` vit dans un volume Docker, qui masque l'image : reconstruire ne
suffit pas, il faut recréer le volume.

```bash
# Backend (requirements.txt)
docker compose build backend && docker compose up -d backend

# Frontend (package.json) : mettre à jour le lockfile, rebuild, recréer le volume
docker compose exec frontend npm install --package-lock-only
docker compose build frontend
docker compose rm -sf frontend
docker volume rm blueprint-academy_frontend_node_modules blueprint-academy_frontend_next_cache
docker compose up -d frontend
```

### Derrière un proxy d'inspection TLS

Si `pip` ou `npm` échouent au build avec `CERTIFICATE_VERIFY_FAILED`, déposer le
certificat racine de votre proxy dans [certs/](certs/README.md) et relancer le
build. Le dossier peut rester vide sur un réseau sans proxy.

## Structure

```
.
├── docker-compose.yml
├── .env.example
├── CLAUDE.md                  # source de vérité du projet
├── certs/                     # CA d'entreprise optionnels (proxy TLS)
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh          # attente PostgreSQL + migrations
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── settings/          # base.py, dev.py, prod.py, env_utils.py
│   │   ├── urls.py            # racine
│   │   ├── api_urls.py        # routes sous /api/
│   │   └── views.py           # sonde /api/health/
│   ├── common/                # abstractions partagées (pas une app Django)
│   │   ├── models.py          # TimeStampedModel, PublishableModel, OrderedModel
│   │   ├── enums.py           # Difficulty, CompletionStatus
│   │   ├── schemas.py         # graphe normalisé + helper de validation JSON
│   │   └── content_blocks.py  # grammaire des blocs de contenu rédactionnel
│   └── apps/                  # une app par domaine métier
│       ├── users/             # User (AUTH_USER_MODEL), rôle, Profile
│       ├── learning/          # Skill, LearningPath, Module, Lesson
│       ├── exercises/         # Exercise (types A–I), ExerciseAttempt
│       │                      #   enums.py = taxonomie, schemas/ = contrats JSON
│       │                      #   validators/ = registre (Phase 2b)
│       ├── progress/          # LessonProgress, CourseProgress, SkillMastery
│       ├── gamification/      # XPTransaction (ledger), Achievement
│       ├── projects/          # Project, ProjectProgress
│       └── validation/        # service isolé (interfaces, Phase 2b)
└── frontend/
    ├── Dockerfile
    ├── app/                   # App Router
    ├── components/
    ├── lib/                   # client API, hooks
    └── stores/                # Zustand
```

Chaque app backend suit la même arborescence : `models.py`, `admin.py`,
`services/` (**toute** la logique métier), `tests/`.

## Conventions

- **Couche service obligatoire** : la logique métier vit dans
  `apps/<app>/services/`, jamais dans les vues ni les modèles.
- **Contenu pédagogique piloté depuis l'admin**, sans toucher au code : tout
  `content` / `solution` est validé par un schéma JSON à la sauvegarde.
- **La pratique prime** : seuls les exercices de production (types E/F/G/H/I,
  `is_practice=True`) font progresser la maîtrise et déverrouillent les
  prérequis. La règle est verrouillée par une contrainte en base.
- **Pondération XP configurable** via `EXERCISE_XP_DEFAULTS` (settings ou
  variable d'environnement), jamais en dur dans le code métier.
- **Secrets en variables d'environnement** : `.env` n'est jamais commité.
- **Auth** : access token JWT gardé en mémoire côté client, refresh token en
  cookie httpOnly (rotation activée) — réglages dans
  `config/settings/base.py` (`SIMPLE_JWT`, `JWT_REFRESH_COOKIE`).

## Développement sans Docker (optionnel)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
POSTGRES_HOST=localhost POSTGRES_PORT=5434 python manage.py migrate
POSTGRES_HOST=localhost POSTGRES_PORT=5434 python manage.py runserver

# Frontend
cd frontend
npm install
npm run dev
```

Une instance PostgreSQL doit être disponible (`docker compose up postgres`
suffit).
