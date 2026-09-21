# CLAUDE.md — Blueprint Learning Platform

> Fichier de contexte permanent. À lire en entier à chaque session. C'est la
> **source de vérité** du projet. Les décisions marquées « verrouillées » ne se
> changent pas sans validation explicite du propriétaire.

## Vision

Plateforme web d'apprentissage **pratique** d'Unreal Engine **Blueprint**.
Philosophie : **Learn → Practice → Build → Validate → Progress**.
Ce n'est **pas** une plateforme vidéo : l'utilisateur apprend en faisant des
exercices, des défis, puis des projets. L'architecture doit permettre de partir
de « je ne sais pas ce qu'est Blueprint » jusqu'à « je peux concevoir un jeu
complet en Blueprint ». Le MVP est petit ; le socle doit être extensible.

## Stack (décisions verrouillées)

- **Backend** : Python 3.12, Django 5 + Django REST Framework.
- **Auth** : JWT via `djangorestframework-simplejwt`. Refresh token en cookie
  **httpOnly**, access token gardé en mémoire côté client. Rotation des refresh.
- **DB** : PostgreSQL.
- **Frontend** : Next.js (App Router) + TypeScript + Tailwind + TanStack Query
  (état serveur) + Zustand (état client léger).
- **Éditeur graphique** (exercices types E/G) : React Flow (`@xyflow/react`).
- **Drag & drop** (types C/D) : dnd-kit.
- **Conteneurisation** : Docker + `docker compose` (services : postgres, backend, frontend).

## Architecture backend — règles

- Apps Django séparées : `users`, `learning`, `exercises`, `progress`,
  `gamification`, `projects`, `validation`. Jamais tout dans une seule app.
- **Couche service obligatoire** : la logique métier vit dans
  `apps/<app>/services/`, **jamais** dans les vues ni les modèles. Les vues DRF
  se contentent de valider / sérialiser / déléguer.
- **Contenu pédagogique séparé du code** : on doit pouvoir créer/modifier
  parcours, modules, leçons et exercices depuis l'admin **sans toucher au code
  ni au frontend**.

## Modèle de données — points structurants

- **`Skill` (Concept)** = entité de 1er ordre, **orthogonale** à
  Path/Module/Lesson. Une Lesson enseigne des Skills ; un Exercise pratique des
  Skills ; **les prérequis se déclarent en Skills**, pas en Lessons.
- **`Exercise` = un seul modèle polymorphe** : `type` (A–G) + `content`
  (JSONField) + `solution` (JSONField). **Pas 7 modèles.** Un schéma JSON
  validé à la sauvegarde par type d'exercice.
- **XP = ledger** : `XPTransaction` est la **source de vérité** ;
  `Profile.total_xp` n'est qu'un cache dénormalisé.
- **`SkillMastery`** (user, skill, mastery_score) pour la maîtrise :
  « leçon terminée » ≠ maîtrise.
- **Leaderboards = requêtes calculées** sur `XPTransaction`. **Pas de table**
  dédiée au MVP.
- **`Challenge` n'est pas une entité séparée au MVP** : c'est un `Exercise`
  type G avec des flags. La vraie entité `Challenge` arrive en V3 (time trials).

Entités MVP : `User`, `Profile`, rôle (Student/Instructor/Admin),
`LearningPath`, `Module`, `Lesson`, `Skill`, `Exercise`, `ExerciseAttempt`,
`LessonProgress`, `CourseProgress`, `SkillMastery`, `XPTransaction`,
`Achievement`, `UserAchievement`, `Project`, `ProjectProgress`.

## Validation des exercices — architecture (critique)

- App `validation` **isolée** du reste. **Registre de validateurs** :
  `exercise_type → Validator`.
- Interface : `Validator.validate(exercise, submission) -> ValidationResult(is_correct, score, feedback, hints[])`.
- Types **E** (construction logique) et **G** (challenge) : la solution ET la
  soumission sont un **graphe normalisé** :
  `{ "nodes": [{"id","type"}], "edges": [{"from","to","pin"}] }`.
  La validation vérifie **présence de nodes / connexions / variables / types**.
- Ce validateur de graphe est le **prototype** de la future validation de vrais
  projets Blueprint (V2) : l'utilisateur collera le **texte exporté des nodes
  UE** (copier-comme-texte), **jamais** de parsing binaire `.uasset`.
- Toujours vérifier des **propriétés** (tel node présent, telle connexion
  existe), **jamais** « exactement ce graphe » — sinon faux négatifs sur des
  solutions valides.
- Le futur **tuteur IA** (V2) se greffe ici : après un `ValidationResult` en
  échec, un `HintService` produit des indices progressifs
  (hint 1 → hint 2 → explication → solution). Prévoir l'**interface**
  maintenant, pas l'implémentation.

## Frontend — règles

- Vitrine publique (landing, catalogue) en SSR/SSG pour le SEO ; app
  authentifiée en Client Components.
- Composant unique **`<ExerciseWorkspace type=…>`** qui route vers le rendu par
  type (A–G).
- Le canvas React Flow (types E/G) est la **fondation** du futur Blueprint
  Playground : le concevoir extensible dès le départ.
- UI : **sombre**, orientée dev/gaming, professionnelle, lisible, responsive
  (cible principale = **PC**). Identité inspirée d'Unreal **sans copier** son
  branding. Gamification visuelle **avec modération** — la priorité reste
  l'apprentissage.

## API REST

- Préfixe `/api/`. Endpoints : `auth`, `users`, `learning-paths`, `modules`,
  `lessons`, `exercises`, `exercises/{id}/submit`, `progress`, `achievements`,
  `projects`.
- Permissions par rôle : **Student / Instructor / Admin**.

## Sécurité

- Validation backend systématique, permissions par rôle, CORS correctement
  configuré, rate limiting là où pertinent (V3), secrets en variables
  d'environnement (`.env`, **jamais** commité), gestion sûre des uploads.

## Roadmap (livrer P0 d'abord ; ne pas anticiper P2+)

- **MVP (P0)** : auth, profil, paths/modules/lessons, exercises A–G
  (validateurs simples), progression + prérequis Skill, XP + niveaux, mastery
  basique, dashboard, admin de contenu, seed « Blueprint Fundamentals »,
  Docker, tests.
- **P1** : achievements, streak, mastery, stats basiques.
- **V2** : Blueprint Playground, projets + validation par graphe collé, tuteur IA.
- **V3** : time trials, leaderboards, saisons, rate-limiting (Redis).
- **V4** : tournois, communauté, équipes, projets publics / showcase.

## Méthode de travail (impératif)

- **Travailler par phases, une seule à la fois** :
  1. Architecture + config · 2. Backend · 3. Frontend · 4. Admin ·
  5. Seed data · 6. Tests · 7. Docker · 8. Documentation.
- À chaque phase : implémenter → tester → corriger → vérifier → **attendre
  validation** avant de continuer.
- **Ne pas générer des milliers de fichiers d'un coup.** Incrémental.
- Ne **jamais** sacrifier la qualité architecturale pour ajouter des features au MVP.
- Qualité : séparation des responsabilités, DRY, SOLID quand pertinent, typage
  TS strict, noms explicites, tests, documentation des parties complexes.

## Structure du projet

```
blueprint-platform/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/            # settings (base/dev/prod), urls, asgi/wsgi
│   └── apps/
│       ├── users/         # models, serializers, views, services/, tests/
│       ├── learning/
│       ├── exercises/     # + validators/ (registre)
│       ├── progress/
│       ├── gamification/
│       ├── projects/
│       └── validation/    # service isolé
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── app/               # routing Next
    ├── components/
    ├── lib/               # client API, hooks
    └── stores/            # Zustand
```

## Commandes

- Dev : `docker compose up --build`
- Migrations : `docker compose exec backend python manage.py makemigrations && docker compose exec backend python manage.py migrate`
- Superuser : `docker compose exec backend python manage.py createsuperuser`
- Seed : `docker compose exec backend python manage.py seed_blueprint`
- Tests backend : `docker compose exec backend pytest`
- Tests frontend : `docker compose exec frontend npm test`

## Pédagogie (ne pas négliger)

Chaque concept doit répondre à : **Qu'est-ce que c'est ? Pourquoi existe-t-il ?
Quand l'utiliser ? Comment l'utiliser ? Quelle erreur fait le débutant ? Comment
est-ce utilisé dans un vrai jeu ?** Le contenu d'une Lesson est **structuré**
(JSON par blocs), pas du texte libre. Éviter les longs blocs de texte :
explications courtes, exemples, interactions, exercices.

**Risque nº 1 du projet = justesse du contenu Blueprint.** Chaque exercice doit
être vérifiable sur un vrai projet Unreal avant publication.
