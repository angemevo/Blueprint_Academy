"""Reglages de developpement local et docker compose."""

from .base import *  # noqa: F401,F403
from .base import JWT_REFRESH_COOKIE as _JWT_REFRESH_COOKIE
from .env_utils import env_bool, env_list

DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1", "0.0.0.0", "backend"]
)

# En dev, pas de HTTPS : le cookie de refresh ne peut pas etre `Secure`.
JWT_REFRESH_COOKIE = {**_JWT_REFRESH_COOKIE, "SECURE": False}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
