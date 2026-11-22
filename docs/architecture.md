# Architecture

Ce document décrit le code tel qu'il est aujourd'hui. Les règles de fond
(décisions verrouillées) sont dans [CLAUDE.md](../CLAUDE.md).

## Les apps backend

| App | Rôle |
|---|---|
| `users` | `User` (rôle `student` / `instructor` / `admin`), `Profile` (XP et niveau en cache), inscription, connexion, refresh, déconnexion. |
| `learning` | Contenu : `Skill`, `LearningPath`, `Module`, `Lesson`. Lecture du catalogue, publication avec contrôle d'intégrité, seed. |
| `exercises` | `Exercise` (un modèle pour les types A à I), `ExerciseAttempt`, schémas JSON, validateurs de soumission, soumission. |
| `progress` | `LessonProgress`, `CourseProgress`, `SkillMastery` ; calcul de la maîtrise, verrouillage des leçons, tableau de bord. |
| `gamification` | `XPTransaction` (le ledger d'XP), niveaux, `Achievement` (modèles). |
| `projects` | Modèles `Project` et `ProjectProgress` seulement : pas encore de service ni d'API. |
| `validation` | App **isolée** : uniquement les contrats (`Validator`, `ValidationResult`, `HintService`) dans `interfaces.py`. |

`common/` n'est pas une app : modèles de base, schéma du graphe normalisé,
blocs de contenu des leçons, catalogue de nodes (`blueprint_catalog.py`).

La taxonomie des exercices vit uniquement dans `apps/exercises/enums.py`.
Les barèmes et seuils (XP, niveaux, maîtrise, contrôle d'intégrité) vivent dans
`config/settings/base.py` : `EXERCISE_XP_DEFAULTS`, `XP_LEVEL_THRESHOLDS`,
`MASTERY_SETTINGS`.

## Couche service

Les vues (`views.py`) valident l'entrée, appellent un service, sérialisent la
réponse. La logique est dans `apps/<app>/services/` :

- `exercises/services/submission.py` : soumission d'un exercice ;
- `exercises/services/graph_validation.py` : vérification d'un graphe ;
- `gamification/services/xp.py` : ledger, cache, niveau ;
- `progress/services/mastery.py` : maîtrise des Skills ;
- `progress/services/lessons.py` : verrouillage, démarrage et fin de leçon ;
- `learning/services/integrity.py` et `publication.py` : publication.

Les imports vers `validation` depuis `exercises` sont **locaux à la fonction**
(par exemple dans le validateur de graphe), pour garder `validation` isolée.

## Flux d'une soumission

`POST /api/exercises/<id>/submit/` (utilisateur connecté) :

```
Client                Vue (ExerciseSubmitView)
  | submission, durée, indices
  |------------------------>  exercice visible pour ce rôle ?  (sinon 404)
                              |
                              v
                     submit_exercise()  [transaction atomique]
                       1. get_validator(type)      -> pas de validateur : 501
                       2. verrou sur l'utilisateur, lecture des tentatives
                       3. max_attempts atteint ?   -> 409
                       4. validator.validate()     -> ValidationResult
                       5. création de ExerciseAttempt (numéro alloué ici)
                       6. si correct : award_exercise_xp()
                              -> XPTransaction (une seule fois par exercice)
                              -> Profile.total_xp / level recalculés (cache)
                       7. si exercice de production : update_skill_mastery()
                              -> SkillMastery de chaque Skill de l'exercice
  |<------------------------  résultat + numéro de tentative
```

Points à retenir :

- **Validateurs** : un registre `type -> validateur` (`exercises/validators/`).
  Aujourd'hui : A, B, C, D (rappel) et E, F, G, H (graphe, via
  `graph_validation.py`). Le type **I n'a pas encore de validateur** : la
  soumission répond 501.
- **Tentative** : le numéro est alloué dans la transaction, sous verrou, pour
  que deux soumissions simultanées n'obtiennent pas le même numéro. La
  tentative garde soumission, score, retours, indices consultés et durée.
- **XP** : le ledger `XPTransaction` fait foi ; l'XP d'un exercice n'est
  créditée qu'à la première réussite. `Profile.total_xp` et `level` sont un
  cache. `manage.py recompute_xp` le reconstruit depuis le ledger.
- **Maîtrise** : seuls les exercices de production la font bouger. Pour
  chaque exercice non-I, on retient la meilleure réussite (base, bonus selon
  le numéro de tentative, bonus de vitesse, moins une pénalité par indice) ;
  la maîtrise est la moyenne pondérée de ces qualités, ramenée sur 100. Le
  type I n'ajoute qu'un bonus plafonné : 100 % reste atteignable sans lui. Un
  échec ne fait jamais baisser la maîtrise acquise. Tous les chiffres sont dans
  `MASTERY_SETTINGS`.
- **La `solution` n'est jamais envoyée au client** (`exercises/services/
  catalog.py`) ; les items des types C et D sont mélangés côté serveur.
- **Visibilité** : un étudiant ne voit que le contenu publié (exercice, leçon,
  module et parcours). Formateur et administrateur voient aussi le brouillon.

## Verrouillage par prérequis de Skills

Un prérequis se déclare en **Skills**, jamais en leçons.

```
Leçon L  enseigne les Skills {S1}
         exige   Lesson.required_skills        {S2}
              + Skill.prerequisites de S1      {S3}
         (moins les Skills qu'elle enseigne elle-même)

L est accessible  <=>  S2 et S3 sont maîtrisées par l'utilisateur
Skill maîtrisée   <=>  SkillMastery.mastery_score >= mastered_threshold (80)
```

`progress/services/lessons.py` : `start_lesson` et `complete_lesson`
refusent une leçon verrouillée (`LessonLocked`, avec la liste des Skills
manquantes) ; `GET /api/progress/` indique quelles leçons sont verrouillées. Comme la maîtrise ne vient que des exercices de production,
**réussir un rappel (A/B/C/D) ne déverrouille rien**.

Remarque : `LearningPath.required_skills` existe dans le modèle, mais aucun
code ne l'applique aujourd'hui.

## Routes de l'API

Sous `/api/` (`config/api_urls.py`) : `auth/` (register, login, refresh,
logout), `users/me/`, `learning-paths/` et `learning-paths/<slug>/`,
`lessons/<id>/` (+ `start/`, `complete/`), `progress/` et `progress/dashboard/`,
`exercises/<id>/` (+ `submit/`), `node-catalog/`, `health/`.

## Frontend

Next.js (App Router) : pages `catalogue`, `connexion`, `inscription`,
`mon-espace`, leçon et exercice sous `catalogue/<slug>/lecons/<id>/`. Le
composant `ExerciseWorkspace` route par type d'exercice ; le canvas de nodes
(React Flow) est dans `components/blueprint-*.tsx`. L'état serveur passe par
TanStack Query, la session par un store Zustand.
