# CLAUDE.md — Blueprint Learning Platform

> Fichier de contexte permanent. À lire en entier à chaque session. C'est la
> **source de vérité** du projet. Les décisions marquées « verrouillées » ne se
> changent pas sans validation explicite du propriétaire.

## Vision

La plateforme est une **école** qui forme à Unreal Engine **Blueprint** par la
pratique. Son public : des personnes qui n'ont **pas forcément la machine**
pour faire tourner Unreal Engine. Sa promesse : qu'un étudiant soit
**opérationnel dès son entrée dans Unreal**.

- Ce n'est **pas** une plateforme vidéo : on apprend en faisant.
- Ce n'est **pas** un substitut à Unreal : le succès se mesure à ce que
  l'étudiant sait faire **le jour où il ouvre l'éditeur**, pas à ce qu'il
  construit sur la plateforme.
- Sur le long terme, apprendre doit aussi être **amusant** : contre-la-montre,
  concours, puzzles, énigmes (voir « Modes ludiques »).

Philosophie : **Learn → Practice → Build → Validate → Progress**.

## Principes directeurs (verrouillés)

1. **La pratique prime.** On ne progresse qu'en produisant. Le rappel (question,
   QCM) sert d'échauffement et ne prouve jamais la maîtrise.
2. **Fidélité à Unreal.** Tout ce qui est pratiqué doit se transférer tel quel
   dans l'éditeur UE5 : mêmes noms de nodes, de pins et de catégories, mêmes
   conventions visuelles, mêmes gestes. En cas de doute, **Unreal a raison**.
   Mieux vaut ne pas enseigner une chose que l'enseigner approximativement.
3. **Aucun prérequis matériel.** Tout le parcours est réalisable dans le
   navigateur, sans Unreal installé. Aucun Skill, aucun déverrouillage ne peut
   dépendre d'un exercice qui exige Unreal.
4. **Le fun sert l'apprentissage.** Chaque mécanique ludique (chrono, score,
   classement, puzzle) doit entraîner une compétence transférable dans Unreal.
   Pas de mécanique gratuite.
5. **Légèreté.** Le public a souvent des machines modestes et des connexions
   limitées : bundle raisonnable, peu de données transférées, rendu sobre.

## Stack (verrouillée)

- **Backend** : Python 3.12, Django ≥ 5.1 + Django REST Framework.
- **Auth** : JWT via `djangorestframework-simplejwt`. Refresh token en cookie
  **httpOnly**, access token en mémoire côté client. Rotation des refresh.
- **DB** : PostgreSQL.
- **Frontend** : Next.js (App Router) + TypeScript + Tailwind + TanStack Query
  (état serveur) + Zustand (état client léger).
- **Canvas de nodes** : React Flow (`@xyflow/react`). **Central au MVP.**
- **Drag & drop** (types C/D) : dnd-kit.
- **Validation JSON** : `jsonschema` (Draft 2020-12).
- **Conteneurisation** : Docker + `docker compose` (postgres, backend, frontend).

## Architecture backend — règles

- Apps Django séparées : `users`, `learning`, `exercises`, `progress`,
  `gamification`, `projects`, `validation`. Jamais tout dans une seule app.
- **Couche service obligatoire** : la logique métier vit dans
  `apps/<app>/services/`, **jamais** dans les vues ni les modèles.
- **Contenu pédagogique séparé du code** : parcours, modules, leçons et
  exercices se créent depuis l'admin **sans toucher au code**.
- L'app `validation` est **isolée** : tout import vers elle depuis `exercises`
  reste **local à la fonction**.

## Modèle de données — points structurants

- **`Skill` (Concept)** : entité de 1er ordre, orthogonale à
  Path/Module/Lesson. Les **prérequis se déclarent en Skills**.
- **`Exercise`** : un seul modèle polymorphe (`type` + `content` + `solution`
  en JSON). `is_practice` est **dérivé** de la taxonomie et verrouillé par une
  `CheckConstraint`.
- **XP = ledger** : `XPTransaction` est la source de vérité ;
  `Profile.total_xp` n'est qu'un cache. Barème **configurable**
  (`settings.EXERCISE_XP_DEFAULTS`), jamais en dur.
- **`SkillMastery`** : ne progresse **que** sur des exercices de production.
- **`ExerciseAttempt`** : conserve tout (soumission, score, durée, indices,
  numéro de tentative). C'est la matière première de la maîtrise, des
  statistiques et des futurs modes ludiques. Le numéro de tentative est
  **alloué par le service dans une transaction**.
- **Leaderboards = requêtes calculées** sur `XPTransaction` et
  `ExerciseAttempt`. Pas de table dédiée avant la V3.
- **`Challenge`** : pas d'entité séparée avant la V3 ; au MVP, c'est un
  `Exercise` type G avec des flags.

## Exercices — taxonomie

| Type | Intitulé | Famille | Valide la maîtrise ? |
|------|----------|---------|----------------------|
| A | Question | rappel | non |
| B | QCM | rappel | non |
| D | Node matching | rappel | non |
| C | Remettre dans l'ordre | transition | non |
| F | Debugging (corriger un graphe) | production | **oui** |
| E | Construction logique (graphe libre) | production | **oui** |
| G | Challenge (objectif → construire) | production | **oui** |
| H | Compléter le graphe | production | **oui** |
| I | Réaliser dans Unreal + coller l'export | production | **oui** |

Règles :

- A/B/D : échauffements courts, XP faible, ne valident ni ne déverrouillent rien.
- Production contrainte (H, F) **avant** le free-build (E, G).
- **Type I = épreuve de passage, toujours optionnelle.** C'est la preuve que
  l'étudiant sait refaire dans le vrai Unreal ce qu'il a appris. **Chaque Skill
  doit pouvoir être maîtrisé sans exercice de type I.**
- Source de vérité de la taxonomie : `apps/exercises/enums.py`. Ne jamais
  redéclarer ces listes ailleurs.

## Catalogue de nodes (verrouillé)

- `common/blueprint_catalog.py` est le **vocabulaire unique** de la
  plateforme. Il s'applique à **tous** les types de production : palettes,
  graphes fournis, solutions.
- Les identifiants doivent être **dérivables mécaniquement du texte exporté
  par l'éditeur UE5** (`Class=...`, `MemberName=...`). Un vrai export UE5 sert
  de fixture de test.
- Les noms affichés sont **identiques** à ceux de l'éditeur UE5.
- Extension sans livrer de code : `BLUEPRINT_EXTRA_NODE_TYPES`.
- Évolution prévue : le catalogue décrira aussi les **pins** de chaque node
  (nom, direction, type) et sera servi par l'API au canvas. Il devient alors la
  source unique pour la validation, le rendu et, plus tard, l'exécution.

## Validation des exercices (critique)

- **Deux niveaux à la sauvegarde** (`apps/exercises/schemas/`) : schéma JSON,
  puis contrôles de **cohérence** (exercice soluble, ids uniques, références
  valides, erreurs rangées sous le bon champ).
- **Registre de validateurs de soumission** : `exercise_type → Validator`,
  interface `validate(exercise, submission) -> ValidationResult(is_correct, score, feedback, hints[])`.
- **Graphe normalisé** :
  `{"nodes": [{"id", "type", ...}], "edges": [{"from", "to", "from_pin", "to_pin"}]}`.
  Pins : **uniquement `from_pin` / `to_pin`**.
- **Solution = propriétés à vérifier, jamais un graphe exact.** Sélecteurs de
  node avec `match` sur les propriétés (variable, fonction…), réutilisés pour
  les connexions (`from` / `to`).
- **Au moins une exigence positive** par solution de production
  (`required_nodes`, `required_edges` ou `required_variables`).
- **Nodes verrouillés vérifiés côté serveur**, jamais seulement par le canvas.
- **Un exercice F/H déjà résolu par son graphe de départ est refusé** à la
  sauvegarde (à brancher dès que le validateur de graphe existe).
- Type I : le texte exporté d'Unreal est normalisé en graphe, puis validé par
  le même moteur. **Jamais** de parsing binaire `.uasset`.
- Tuteur IA (V2) : un `HintService` se branche après un échec
  (indice 1 → indice 2 → explication → solution). Interface prévue, pas
  d'implémentation au MVP.
- **La `solution` n'est jamais envoyée au client** avant soumission. Les items
  du type C sont **mélangés côté serveur**.

## Frontend — règles

- Vitrine publique (landing, catalogue) en SSR/SSG ; app authentifiée en
  Client Components.
- Composant unique **`<ExerciseWorkspace type=…>`** qui route par type.
- **Le canvas est un simulateur d'entraînement**, comme un simulateur de vol :
  l'espace de travail ressemble le plus possible à l'éditeur Blueprint
  (forme des nodes, couleur des pins selon le type, pins d'exécution vs de
  données, clic droit pour chercher un node, tirer depuis un pin, compiler).
  L'identité visuelle propre à la plateforme reste **autour** du canvas, sans
  copier le branding d'Epic.
- UI sombre, orientée dev/gaming, lisible, responsive, cible principale PC.
- **Budget de légèreté** : éviter les dépendances lourdes, charger le canvas à
  la demande, pas de 3D au MVP.

## Interpréteur de graphes (V2 — fidèle ou absent)

- Utile pour voir les conséquences d'un graphe et valider par **comportement**
  plutôt que par structure (moins de faux négatifs).
- Règle absolue : **un sous-ensemble exécuté exactement comme Unreal**
  (ordre d'exécution, BeginPlay avant Tick, Delay…) ou rien. Un interpréteur
  approximatif enseigne un modèle mental faux.
- Un seul interpréteur en TypeScript : aperçu dans le navigateur, validation
  qui fait foi dans un petit service Node appelé par l'app `validation`.
- Ce n'est **pas** un moteur de jeu : c'est un laboratoire pédagogique.

## Modes ludiques (long terme)

Objectif : que les étudiants **s'amusent** en apprenant. Règle de conception :
un mode ludique est une **couche au-dessus du moteur d'exercices existant**,
jamais un moteur à part. Il réutilise `Exercise`, les validateurs et
`ExerciseAttempt`.

| Mode | Principe | Compétence Unreal entraînée | Version |
|------|----------|-----------------------------|---------|
| Énigmes | Symptôme en jeu → trouver le bug (base : type F) | lire et déboguer un graphe | V2 |
| Puzzles | Contraintes : nombre de nodes limité, nodes interdits, palette réduite (base : H/E/G) | concevoir proprement, connaître les alternatives | V2 |
| Contre-la-montre | Résoudre un challenge chronométré | gestes et réflexes de l'éditeur | V3 |
| Concours / saisons | Série de challenges avec classement | régularité, polyvalence | V3 |
| Tournois | Qualifications, phases finales, équipes | maîtrise sous pression | V4 |

À préserver dès maintenant (sans rien implémenter) : durée, score, nombre de
tentatives et indices consultés sont enregistrés sur chaque `ExerciseAttempt` ;
les flags de challenge (`time_limit_seconds`, `max_attempts`) restent sur
`Exercise` ; les contraintes de puzzle s'expriment dans la `solution`
(`max_nodes`, `forbidden_nodes`) ou la palette.

## Compétences de sortie

Chaque fin de parcours définit des **compétences observables dans Unreal**
(ex. : « créer un Actor Blueprint avec un système de vie et de dégâts »,
« faire communiquer deux Blueprints par une interface », « afficher une barre
de vie avec un Widget »). Les Skills en sont la traduction technique ; tous les
exercices servent ces compétences.

Le parcours inclut un volet **prise en main de l'éditeur** (Content Browser,
panneau Details, My Blueprint, Compile, lecture d'erreurs) via des maquettes
interactives, puisque l'étudiant ne peut pas ouvrir Unreal à côté.

## API REST

- Préfixe `/api/`. Endpoints : `auth`, `users`, `learning-paths`, `modules`,
  `lessons`, `exercises`, `exercises/{id}/submit`, `progress`, `achievements`,
  `projects`.
- Permissions par rôle : **Student / Instructor / Admin**.

## Sécurité

Validation backend systématique, permissions par rôle, CORS configuré, rate
limiting (V3), secrets en variables d'environnement (`.env` jamais commité),
uploads sécurisés, solutions jamais exposées avant soumission.

## Roadmap (livrer P0 d'abord ; ne pas anticiper)

- **MVP (P0)** : auth, profil, paths/modules/lessons, exercices A–I avec
  validation de structure, progression + prérequis Skill, XP + niveaux,
  maîtrise basique, dashboard, admin de contenu, catalogue de nodes, seed
  « Blueprint Fundamentals », Docker, tests.
- **P1** : achievements, streak, statistiques basiques, maquettes interactives
  de l'éditeur (prise en main).
- **V2** : interpréteur fidèle + validation par comportement, Blueprint
  Playground, énigmes et puzzles, tuteur IA, projets.
- **V3** : contre-la-montre, leaderboards, saisons, concours, rate limiting
  (Redis).
- **V4** : tournois, équipes, communauté, showcase.

## Méthode de travail (impératif)

- Phases, une à la fois : 1. Architecture + config · 2. Backend ·
  3. Frontend · 4. Admin · 5. Seed · 6. Tests · 7. Docker · 8. Documentation.
- À chaque phase : implémenter → tester → corriger → vérifier → **attendre
  validation**.
- Incrémental : pas de milliers de fichiers d'un coup.
- Ne jamais sacrifier la qualité architecturale pour ajouter des features.
- Qualité : séparation des responsabilités, DRY, SOLID si pertinent, typage TS
  strict, noms explicites, tests, documentation des parties complexes.

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
│   ├── common/            # schémas partagés, catalogue de nodes, modèles de base
│   └── apps/
│       ├── users/
│       ├── learning/
│       ├── exercises/     # enums.py, schemas/, validators/
│       ├── progress/
│       ├── gamification/
│       ├── projects/
│       └── validation/    # service isolé
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── app/
    ├── components/
    ├── lib/
    └── stores/
```

## Commandes

- Dev : `docker compose up --build`
- Migrations : `docker compose exec backend python manage.py makemigrations && docker compose exec backend python manage.py migrate`
- Superuser : `docker compose exec backend python manage.py createsuperuser`
- Seed : `docker compose exec backend python manage.py seed_blueprint`
- Tests backend : `docker compose exec backend pytest`
- Tests frontend : `docker compose exec frontend npm test`

## Pédagogie

Chaque concept répond à : **Qu'est-ce que c'est ? Pourquoi existe-t-il ? Quand
l'utiliser ? Comment l'utiliser ? Quelle erreur fait le débutant ? Comment
est-ce utilisé dans un vrai jeu ?** Contenu de leçon structuré (JSON par blocs),
explications courtes, puis très vite un exercice de production. Une leçon ne se
termine pas sur un QCM : elle se termine sur quelque chose que l'étudiant a
construit.

**Risque nº 1 = justesse du contenu Blueprint.** Chaque exercice doit être
vérifiable sur un vrai projet Unreal avant publication.