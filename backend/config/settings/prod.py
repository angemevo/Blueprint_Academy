"""Reglages de production.

Squelette volontairement minimal : durci en Phase 7/8 (deploiement).
"""

from .base import *  # noqa: F401,F403
from .base import JWT_REFRESH_COOKIE as _JWT_REFRESH_COOKIE
from .env_utils import env_bool

DEBUG = False

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

JWT_REFRESH_COOKIE = {**_JWT_REFRESH_COOKIE, "SECURE": True}
