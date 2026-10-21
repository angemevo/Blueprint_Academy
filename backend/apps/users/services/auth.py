"""Services d'authentification : inscription, cookie de refresh, deconnexion."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import Profile, Role, User


@transaction.atomic
def register_user(*, username: str, email: str, password: str) -> User:
    """Cree un etudiant et son Profile. Le role est toujours `student`."""
    user = get_user_model().objects.create_user(
        username=username, email=email, password=password, role=Role.STUDENT
    )
    Profile.objects.create(user=user, display_name=username)
    return user


def set_refresh_cookie(response, refresh: str) -> None:
    cfg = settings.JWT_REFRESH_COOKIE
    response.set_cookie(
        cfg["NAME"],
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=cfg["HTTPONLY"],
        secure=cfg["SECURE"],
        samesite=cfg["SAMESITE"],
        path=cfg["PATH"],
    )


def clear_refresh_cookie(response) -> None:
    cfg = settings.JWT_REFRESH_COOKIE
    response.delete_cookie(cfg["NAME"], path=cfg["PATH"], samesite=cfg["SAMESITE"])


def revoke_refresh(refresh: str | None) -> None:
    """Met le refresh en liste noire ; un token invalide est ignore."""
    if not refresh:
        return
    try:
        RefreshToken(refresh).blacklist()
    except TokenError:
        pass
