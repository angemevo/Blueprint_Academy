"""Modeles de l'app users.

Perimetre : User, Profile, roles (Student / Instructor / Admin).

En Phase 1 on ne declare QUE le modele utilisateur substituable. Django exige
que `AUTH_USER_MODEL` soit fixe avant la toute premiere migration : le changer
ensuite impose de recreer la base. Le reste (Profile, role, avatar, ...) arrive
en Phase 2.
"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Utilisateur de la plateforme.

    Strictement identique a `django.contrib.auth.models.User` pour le moment ;
    sert de point d'extension pour les champs metier de la Phase 2.
    """

    class Meta(AbstractUser.Meta):
        db_table = "users_user"
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
