Titre: Authentification JWT : inscription, connexion, rafraîchissement, déconnexion
Labels: phase-2b,backend
---
**Dépend de :** aucune

## Pourquoi
Prérequis de toute l'app authentifiée. CLAUDE.md fixe le cadre : JWT simplejwt, refresh en cookie httpOnly, access en mémoire côté client, rotation des refresh.

## Ce qui est attendu
- `POST /api/auth/register/` : crée l'utilisateur (rôle `student` imposé, jamais choisi par le client) et son `Profile`, via un service de l'app `users`.
- `POST /api/auth/login/` : renvoie l'access token dans le corps ; pose le refresh token en cookie selon `settings.JWT_REFRESH_COOKIE` (nom, httpOnly, secure, samesite, path).
- `POST /api/auth/refresh/` : lit le refresh **uniquement dans le cookie**, applique la rotation, repose le nouveau cookie, renvoie le nouvel access.
- `POST /api/auth/logout/` : supprime le cookie.
- Validation du mot de passe avec les validateurs Django configurés.

**Décision à valider par Ange avant `ready`** : activer l'app `rest_framework_simplejwt.token_blacklist` et `BLACKLIST_AFTER_ROTATION = True`, pour qu'un refresh volé ou déconnecté ne soit plus réutilisable. Recommandé. Cela ajoute une app et ses migrations dans les settings.

## Critères d'acceptation
- [ ] Le refresh token n'apparaît jamais dans un corps de réponse JSON (test).
- [ ] Refresh sans cookie → 401 ; refresh avec un ancien token après rotation → 401 si la blacklist est activée.
- [ ] Inscription avec `"role": "admin"` dans le corps → rôle `student` (test).
- [ ] Le `Profile` est créé à l'inscription.
- [ ] Tests d'API pour les quatre endpoints, cas nominaux et d'erreur.

## Hors périmètre
- Mot de passe oublié, vérification d'email, connexion sociale.
- Rate limiting (V3).
- Frontend.
