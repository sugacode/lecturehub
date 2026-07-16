import os

from .base import *  # noqa: F401,F403

DEBUG = False

# Trust the reverse proxy's X-Forwarded-Proto header to tell whether the
# original request was HTTPS. Without this, SECURE_SSL_REDIRECT below
# thinks every request is plain HTTP (since gunicorn itself only ever
# speaks HTTP to nginx/Apache) and redirect-loops forever, even though the
# browser is already on HTTPS. Both the nginx and Apache configs in
# docs/DEPLOY_VPS_UBUNTU.md set this header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

if not os.environ.get("DJANGO_ALLOWED_HOSTS"):
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be set in production")
