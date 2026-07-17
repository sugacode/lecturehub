from .dev import *  # noqa: F401,F403

# django-simple-captcha reads this module-level at import time (when the
# "captcha" app loads, early in Django's app registry setup) rather than
# dynamically per-request, so it has to be set here — setting it later from
# tests/conftest.py has no effect, since the app is already imported by then.
CAPTCHA_TEST_MODE = True
