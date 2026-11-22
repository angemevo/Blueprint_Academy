# Guide du contenu : créer un parcours depuis l'admin

Tout le contenu pédagogique se crée dans l'admin Django, sans toucher au code :
http://localhost:8000/admin/ (compte créé avec `createsuperuser`, voir le
[README](../README.md)).

> Justesse Unreal : tout ce qu'on enseigne doit être vérifiable dans le vrai
> éditeur. Rien de ce guide ne garantit qu'un contenu est juste : relire chaque
> exercice dans un vrai projet Unreal avant de le publier.

## Ordre de création

Du plus général au plus fin ; chaque étape s'appuie sur la précédente.

1. **Skills** (section Learning, « skills ») : les compétences. Nom, catégorie,
   difficulté. Le champ *prérequis* liste les Skills à maîtriser avant
   celle-ci.
2. **Parcours** (section Learning, « parcours ») : titre, sous-titre, difficulté, ordre.
3. **Modules** : ajoutés dans le parcours (tableau en bas) ou séparément.
4. **Leçons** : ajoutées dans le module. Une leçon enseigne des Skills
   (*skills_taught*) et peut en exiger d'autres (*required_skills*). Les
   prérequis se déclarent toujours en Skills, jamais en leçons.
5. **Exercices** (section Exercises) : rattachés à une leçon (ou autonomes, par
   exemple un challenge).

Le slug se remplit tout seul depuis le titre. Les cases *ordre* des listes sont
modifiables directement.

Tout est créé **non publié**. Un étudiant ne voit que ce qui est publié, y
compris toute la chaîne : un exercice n'apparaît que si sa leçon, son module et
son parcours le sont aussi. Formateurs et administrateurs voient tout, brouillons
compris.

## Écrire une leçon

Le champ *contenu* est un JSON : une liste de blocs. Types de blocs acceptés :
`heading`, `text`, `list`, `code`, `callout`, `image`, `graph`, `key_points`,
`self_check`. Exemple :

```json
[
  {"type": "heading", "text": "Les variables", "level": 2},
  {"type": "text", "text": "Une variable garde une valeur."},
  {"type": "self_check", "question": "À quoi sert-elle ?", "answer": "À mémoriser une valeur."}
]
```

Un contenu invalide est refusé à l'enregistrement, avec un message sous le
champ. La grammaire exacte est dans `backend/common/content_blocks.py`. Les
trames de leçon suivent les six questions de `CLAUDE.md` (« Pédagogie »), puis
mènent très vite à un exercice de production.

## Écrire un exercice

Choisir le **type** (A à I) ; la famille (rappel, transition, production) en
découle, elle ne se règle pas à la main. Remplir *contenu* (l'énoncé et ses
données), *solution* (la réponse attendue) et, si on veut, *indices* (du plus
léger au plus explicite).

- **A, B, C, D** : rappel et transition. Courts, XP faible, ils **ne font pas
  progresser la maîtrise** et ne déverrouillent rien.
- **E, F, G, H** : production, corrigée sur un graphe. La solution n'est jamais
  un graphe exact : ce sont des **propriétés à vérifier** (nodes requis,
  connexions requises, variables), avec au moins une exigence positive. Les
  nodes ne se choisissent que dans le catalogue (`common/blueprint_catalog.py`).
  F et H partent d'un graphe fourni dont des nodes peuvent être verrouillés ;
  la vérification a lieu côté serveur.
- **I** : réalisation dans Unreal. Épreuve toujours optionnelle. **Elle n'est
  pas encore corrigée par la plateforme** : ne pas en publier avant que ce
  soit le cas.

Renseigner aussi :

- *skills pratiqués* : les Skills dont l'exercice fait progresser la maîtrise ;
- *difficulté* et, si besoin, *XP à la réussite* (vide = valeur par défaut du
  type) ;
- pour un challenge : limite de temps, nombre d'essais maximum, mis en avant.

À l'enregistrement, le contenu et la solution sont vérifiés (forme JSON, puis
cohérence : exercice soluble, identifiants uniques, références valides). Les
erreurs s'affichent sous le champ concerné ; rien n'est enregistré tant qu'il
en reste.

## Publication et contrôle d'intégrité

Pour qu'un étudiant puisse **maîtriser** chaque Skill sans jamais ouvrir
Unreal, chaque Skill enseignée doit avoir, parmi les exercices **publiés**, de
production et **hors type I** :

- au moins **3** exercices de production ;
- dont au moins **1** exercice contraint (type F ou H).

(Seuils : `MASTERY_SETTINGS`, clés `min_production_exercises`,
`min_constrained_exercises`, `constrained_types`.)

Comment publier :

1. **Publier d'abord les exercices**, puis la leçon : le contrôle ne compte que
   les exercices déjà publiés.
2. Dans la liste de l'objet, cocher la ligne puis l'action
   **« Publier (avec contrôle d'intégrité) »**, ou cocher *publié* dans le
   formulaire. L'action **« Dépublier »** fait l'inverse.
3. Si une Skill ne passe pas, la publication est **refusée** et l'admin affiche
   un message par problème, par exemple : « Skill « Variables » : 1 exercice(s)
   de production hors type I publie(s), 3 requis. » Rien n'est modifié ;
   corriger puis recommencer.

Ce qui est contrôlé selon l'objet : une **leçon** (ses Skills enseignées), un
**parcours** (les Skills de toutes ses leçons) et, par l'action Publier, un
**module** (les Skills de ses leçons). Un exercice se publie sans contrôle de ce
type.

## Le contenu de départ

`docker compose exec backend python manage.py seed_blueprint` crée le parcours
« Blueprint Fundamentals » : 7 Skills, 4 modules, et pour le premier module
2 leçons et 6 exercices. Tout est **non publié** : c'est une proposition à
valider, et rien n'y est présenté comme vérifié dans Unreal. La commande est
idempotente : la relancer ne duplique rien et n'écrase pas vos modifications.
