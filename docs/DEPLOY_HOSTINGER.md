# Deploying to Hostinger (hPanel "Setup Python App")

This covers Hostinger's shared/Business/Cloud hosting, where hPanel exposes
a **Setup Python App** feature (Passenger-based — the same underlying
mechanism as cPanel's Python App tool). You don't get root/SSH access to
install system packages or run gunicorn/nginx yourself; Passenger runs your
WSGI app for you.

Two things about this environment shaped a couple of small code changes
already made in this repo:

- **No control over the web server's static-file aliases** → added
  [WhiteNoise](https://whitenoise.readthedocs.io/) so Django serves its own
  static files efficiently without needing an Apache/nginx config you don't
  have access to.
- **Same problem for `/media/`** (uploaded photos, documents) → added a
  `SERVE_MEDIA_VIA_DJANGO` env flag that, when `True`, makes
  `config/urls.py` serve `MEDIA_ROOT` directly even with `DEBUG=False`.
  This is a deliberate simplification appropriate for a low-traffic
  single-user app — not something you'd do on a busy multi-tenant site.

## 1. Check the Python version hPanel offers

hPanel → **Advanced → Setup Python App** → **Create Application**. The
version dropdown shows what's available; pick the closest to 3.12 (3.11 or
3.10 both work fine — nothing in this codebase is 3.12-specific).

## 2. Create the app in hPanel

- **Application root**: e.g. `lecturerhub` (creates `/home/<user>/lecturerhub`)
- **Application URL**: your domain or a subdomain
- **Application startup file**: `passenger_wsgi.py`
- **Application Entry point**: `application`

hPanel creates the app root and a virtualenv, and gives you an "Enter to
the virtual environment" command to paste into its terminal — something like:
```bash
source /home/<user>/virtualenv/lecturerhub/3.11/bin/activate && cd /home/<user>/lecturerhub
```
Keep that command handy — you'll reuse it every time you come back to a
terminal session.

## 3. Get the code in

Use hPanel's **File Manager** to upload a zip of the repo into the app
root and extract it there, or, if Git is available in your terminal:
```bash
git clone <your-repo-url> .
```
(the `.` matters — clone into the existing app root rather than creating a
nested folder, since Passenger expects `passenger_wsgi.py` right there).

## 4. Install dependencies

With the virtualenv active (step 2's command):
```bash
pip install -r requirements.txt
```

## 5. Environment variables

hPanel's Python App page has an **Environment variables** section — prefer
that over a `.env` file where possible, since it's set outside the web
root. Add:

```
DJANGO_SECRET_KEY       = <random string>
DJANGO_SETTINGS_MODULE  = config.settings.prod
DJANGO_ALLOWED_HOSTS    = yourdomain.com,www.yourdomain.com
DEFAULT_ADMIN_USERNAME  = admin
DEFAULT_ADMIN_EMAIL     = you@example.com
DEFAULT_ADMIN_PASSWORD  = <a real password>
SERVE_MEDIA_VIA_DJANGO  = True
```

If hPanel's env var UI doesn't pick these up for some reason, fall back to
a `.env` file in the app root (copy `.env.example`, fill it in) — the app
already loads it via `python-dotenv`.

Leave `DATABASE_URL` unset to keep SQLite (see "Database" below).

**Before this goes live**: confirm SSL is issued and enabled for the domain
(hPanel → SSL, usually auto-provisioned). `config.settings.prod` forces
`SECURE_SSL_REDIRECT = True`, so if the domain isn't actually serving HTTPS
yet, requests will redirect-loop.

## 6. Edit `passenger_wsgi.py`

hPanel generates a stub `passenger_wsgi.py` in the app root. Replace its
contents with:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

If you ended up using a `.env` file instead of hPanel's env var UI, add
before the `get_wsgi_application()` call:
```python
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
```

## 7. Collect static files, migrate, create your account

Still in the virtualenv, from the app root:
```bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_default_user
python manage.py seed_demo   # optional
```

## 8. Restart the app

hPanel's Python App page has a **Restart** button — click it after any
code change, dependency install, or env var edit. (Passenger's classic
`touch tmp/restart.txt` convention also works if you create a `tmp/`
directory in the app root, but the hPanel button is simpler.)

## Database: SQLite vs Hostinger's MySQL

Hostinger includes MySQL databases on shared/Business plans (hPanel →
Databases). For a single lecturer's personal data, **SQLite is simpler and
recommended** — it's a file on the same persistent disk your app already
has, with zero extra setup or connection config.

If you'd rather use the included MySQL: add `mysqlclient` to
`requirements.txt` and set `DATABASE_URL=mysql://user:password@localhost/dbname`
(credentials from hPanel → Databases). Be aware `mysqlclient` compiles a C
extension — if `pip install` fails on missing headers in this environment,
stick with SQLite rather than fighting it.

## Updating after a git push

```bash
# activate the virtualenv (step 2's command), then:
cd /home/<user>/lecturerhub
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then hit **Restart** in hPanel.

## Troubleshooting

- **500 error with no detail** — check hPanel's Python App page for a log
  link/viewer, or temporarily set `DJANGO_DEBUG=True` to see the traceback
  (put it back to `False` immediately after).
- **CSS/Tailwind looks unstyled** — Tailwind/HTMX/Alpine load from a CDN in
  `templates/base.html`, so this usually means the *browser* couldn't reach
  the CDN, not a static-file problem. Django's own static files (admin,
  `static/`) are what `collectstatic` + WhiteNoise handle.
- **Uploaded photos/documents 404** — confirm `SERVE_MEDIA_VIA_DJANGO=True`
  is actually set and the app was restarted after setting it.
- **DOI import (CrossRef) fails** — shared hosting generally allows normal
  outbound HTTPS, so this is more likely a transient CrossRef outage than a
  hosting restriction; the import view already shows the underlying error
  message rather than crashing.
