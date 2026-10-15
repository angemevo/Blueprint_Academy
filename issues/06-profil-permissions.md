Titre: Profil courant et permissions par rôle
Labels: phase-2b,backend
---
**Dépend de :** #05 (authentification)

## Ce qui est attendu
- Classes de permission DRF réutilisables : `IsStudent`, `IsInstructor`, `IsPlatformAdmin`, `IsInstructorOrAdmin`, basées sur `User.role` (pas sur `is_staff`).
- `GET /api/users/me/` : utilisateur et profil courants (`display_name`, `bio`, `avatar_url`, `total_xp`, `level`, séries, `onboarding_completed`).
- `PATCH /api/users/me/` : seuls `display_name`, `bio`, `avatar_url` et `onboarding_completed` sont modifiables. `role`, `total_xp`, `level` et les séries sont en lecture seule.

## Critères d'acceptation
- [ ] Tests des permissions pour chaque rôle.
- [ ] `PATCH` avec `total_xp` ou `role` → valeurs inchangées (test).
- [ ] Non authentifié → 401.

## Hors périmètre
- Profils publics d'autres utilisateurs, classements.
