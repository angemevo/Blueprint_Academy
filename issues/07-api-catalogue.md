Titre: API du catalogue en lecture : parcours, modules, leçons
Labels: phase-2b,backend
---
**Dépend de :** #06 (permissions)

## Ce qui est attendu
- `GET /api/learning-paths/` et `GET /api/learning-paths/{slug}/` : publics (vitrine), parcours publiés seulement, triés par `order`. Le détail inclut les modules publiés et le titre de leurs leçons publiées.
- `GET /api/lessons/{id}/` : authentifié ; renvoie le `content` en blocs, les skills enseignés et les skills prérequis.
- Contenu non publié : visible seulement des rôles Instructor et Admin.
- Requêtes optimisées : pas de N+1 (`select_related` / `prefetch_related`), vérifié par `django_assert_num_queries`.

## Critères d'acceptation
- [ ] Un étudiant ou un visiteur ne voit jamais un contenu non publié (test).
- [ ] Nombre de requêtes borné sur la liste et le détail (test).
- [ ] Pagination DRF par défaut respectée sur la liste.

## Hors périmètre
- Verrouillage par prérequis et progression (issue ultérieure).
- Création ou modification de contenu par API (passe par l'admin).
