"""Base Django settings shared by dev and prod. Loads secrets from environment via python-dotenv."""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me-in-prod")

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"

_raw_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "captcha",
    "apps.accounts",
    "apps.cv",
    "apps.publications",
    "apps.schedule",
    "apps.supervision",
    "apps.research",
    "apps.service",
    "apps.documents",
    "apps.dashboard",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

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
                "apps.dashboard.context_processors.sidebar_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise serves static files straight from the Django process, which
# matters on hosts (e.g. shared/Passenger hosting) where you can't configure
# the web server's own static-file aliases. Harmless everywhere else.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Django doesn't serve MEDIA_ROOT itself outside DEBUG. Most hosts have some
# other way to alias /media/ to disk (nginx, PythonAnywhere's Static files
# UI, etc.); on hosts where you can't configure that (e.g. shared/Passenger
# hosting), set SERVE_MEDIA_VIA_DJANGO=True to have config/urls.py serve it
# directly. Fine for a low-traffic single-user app; not a general-purpose
# production pattern at scale.
SERVE_MEDIA_VIA_DJANGO = os.environ.get("SERVE_MEDIA_VIA_DJANGO", "False") == "True"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "login"

# Auto-logout a day after login. SESSION_SAVE_EVERY_REQUEST is left at its
# default (False), so this is an absolute expiry from login time, not a
# sliding "1 day since last click" window.
SESSION_COOKIE_AGE = 60 * 60 * 24

# Public pages behavior: "open" serves /p/cv/ and /p/schedule/ directly;
# "unlisted" only serves them at the slug-based URLs.
PUBLIC_PAGES_MODE = os.environ.get("PUBLIC_PAGES_MODE", "open")

# django-simple-captcha on the login form, to slow down brute-force login
# attempts. Self-hosted (renders its own distorted-text image, no external
# API/network call), which fits a single-user app better than something like
# reCAPTCHA that requires a Google site key and a call out to google.com on
# every login page load.
CAPTCHA_LENGTH = 5
CAPTCHA_TIMEOUT = 5  # minutes before a challenge expires
CAPTCHA_NOISE_FUNCTIONS = ("captcha.helpers.noise_arcs", "captcha.helpers.noise_dots")
# CAPTCHA_TEST_MODE is turned on in config/settings/test.py so tests don't
# have to solve a real image challenge — see that file for why it can't just
# be set from tests/conftest.py instead.

MAX_UPLOAD_SIZE_MB = 10

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
