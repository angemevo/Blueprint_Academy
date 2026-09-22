"""Reglages communs a tous les environnements.

Les valeurs sensibles ou dependantes de l'environnement sont lues depuis les
variables d'environnement (fichier `.env` a la racine du depot en local).
"""

from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from .env_utils import env_bool, env_int, env_json, env_list, env_str

# backend/config/settings/base.py -> backend/
BASE_DIR = Path(__file__).resolve().parents[2]
# Racine du monorepo, ou vit le .env partage avec docker compose.
REPO_DIR = BASE_DIR.parent

load_dotenv(REPO_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Securite
# ---------------------------------------------------------------------------
SECRET_KEY = env_str("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", ["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", [])

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
]

# Une app par domaine metier. Voir CLAUDE.md > Architecture backend.
LOCAL_APPS = [
    "apps.users",
    "apps.learning",
    "apps.exercises",
    "apps.progress",
    "apps.gamification",
    "apps.projects",
    "apps.validation",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Base de donnees
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env_str("POSTGRES_DB", "blueprint"),
        "USER": env_str("POSTGRES_USER", "blueprint"),
        "PASSWORD": env_str("POSTGRES_PASSWORD", "blueprint"),
        "HOST": env_str("POSTGRES_HOST", "localhost"),
        "PORT": env_str("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": env_int("POSTGRES_CONN_MAX_AGE", 60),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Modele utilisateur personnalise : le remplacer apres la premiere migration
# serait tres couteux. Le role vit sur le User, les donnees pedagogiques sur
# users.Profile.
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Fichiers statiques et medias
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# ---------------------------------------------------------------------------
# JWT : access token en memoire cote client, refresh token en cookie httpOnly
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=env_int("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", 15)
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=env_int("JWT_REFRESH_TOKEN_LIFETIME_DAYS", 7)
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "SIGNING_KEY": SECRET_KEY,
}

# Parametres du cookie porteur du refresh token. Les vues d'auth (Phase 2) les
# consomment ; ils vivent ici pour rester configurables par environnement.
JWT_REFRESH_COOKIE = {
    "NAME": env_str("JWT_REFRESH_COOKIE_NAME", "bp_refresh"),
    "HTTPONLY": True,
    "SECURE": env_bool("JWT_REFRESH_COOKIE_SECURE", not DEBUG),
    "SAMESITE": env_str("JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
    "PATH": "/api/auth/",
}

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS", ["http://localhost:3000", "http://127.0.0.1:3000"]
)
# Necessaire pour que le navigateur envoie le cookie de refresh.
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "root": {"handlers": ["console"], "level": env_str("LOG_LEVEL", "INFO")},
}

# ---------------------------------------------------------------------------
# Pedagogie : ponderation de l'XP par type d'exercice
# ---------------------------------------------------------------------------
# CLAUDE.md : « la pratique prime ». La production doit rapporter bien plus que
# le rappel, et ces valeurs doivent rester CONFIGURABLES, jamais en dur dans le
# code metier. Un exercice peut toujours surcharger la valeur de son type.
# Surcharge possible via la variable d'environnement EXERCISE_XP_DEFAULTS (JSON).
EXERCISE_XP_DEFAULTS = env_json(
    "EXERCISE_XP_DEFAULTS",
    {
        # Rappel (echauffement) : volontairement faible.
        "A": 5,
        "B": 5,
        "D": 5,
        # Transition.
        "C": 15,
        # Production : le coeur du produit.
        "H": 35,
        "F": 40,
        "E": 50,
        "G": 60,
        "I": 60,
    },
)

#: Valeur de repli si un type n'est pas liste ci-dessus.
EXERCISE_XP_FALLBACK = env_int("EXERCISE_XP_FALLBACK", 10)

#: Types de nodes Blueprint acceptes en plus du catalogue de reference
#: (common/blueprint_catalog.py). Permet d'enrichir le garde-fou d'auteur sans
#: livrer de code.
BLUEPRINT_EXTRA_NODE_TYPES = env_list("BLUEPRINT_EXTRA_NODE_TYPES", [])
