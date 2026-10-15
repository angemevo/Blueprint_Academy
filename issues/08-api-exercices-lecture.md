Titre: API exercices en lecture, sans fuite de solution
Labels: phase-2b,backend
---
**Dépend de :** #07 (API catalogue)

## Ce qui est attendu
- `GET /api/exercises/{id}/` : authentifié ; exercice publié ; renvoie `type`, `title`, `content`, `difficulty`, `time_limit_seconds`, `max_attempts`, l'XP effective et le nombre d'indices disponibles.
- **Jamais** `solution`, ni le texte des `hints` (servis plus tard, un par un, via `HintService`).
- Type C : les éléments sont **mélangés côté serveur** à chaque requête ; le mélange ne doit jamais renvoyer l'ordre de la solution quand il y a au moins 2 éléments.
- Exercices rattachés à une leçon listés dans le détail de leçon (titre, type, id), sans contenu.

## Critères d'acceptation
- [ ] Test qui parcourt la réponse JSON entière et vérifie l'absence de toute clé ou valeur de la solution, pour chaque type A à I.
- [ ] Test du mélange du type C.

## Hors périmètre
- Soumission (issue « Soumission d'un exercice »), indices.
