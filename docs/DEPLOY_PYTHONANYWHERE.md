# Deploying to PythonAnywhere

PythonAnywhere gives you a persistent disk (unlike Railway/Render's free
tiers), so LecturerHub's default SQLite database and local `media/` storage
work as-is — no S3, no managed Postgres required for a single-user app.

## 1. Get the code onto PythonAnywhere

Open a **Bash console** (Dashboard → New console → Bash) and either:

```bash
git clone <your-repo-url> lecturerhub
```

or, if the repo is private and you don't want to set up deploy keys, zip
the project locally and upload it via the **Files** tab, then unzip in a
Bash console.

## 2. Create a virtualenv

Check what Python versions are available first:
```bash
ls /usr/bin/python3.*
```
Then, matching the project's target (3.12, or the closest available):
```bash
mkvirtualenv --python=/usr/bin/python3.12 lecturerhub-venv
cd ~/lecturerhub
pip install -r requirements.txt
```
(`mkvirtualenv` is virtualenvwrapper, preinstalled on PythonAnywhere.)

## 3. Configure environment variables

Copy `.env.example` to `.env` and fill it in:
```bash
cp .env.example .env
nano .env
```
Set at minimum:
```
DJANGO_SECRET_KEY=<random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-username>.pythonanywhere.com
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=you@example.com
DEFAULT_ADMIN_PASSWORD=<a real password>
```
Leave `DATABASE_URL` unset — SQLite at `db.sqlite3` is fine and persists on
PythonAnywhere's disk across reloads.

## 4. Configure the web app

Go to the **Web** tab → **Add a new web app** → choose **Manual
configuration** (not the Django quickstart wizard, since this project
already has its own settings split) → pick the same Python version as your
virtualenv.

- **Virtualenv** section: point it at `/home/<username>/.virtualenvs/lecturerhub-venv`
- **Code** section:
  - Source code: `/home/<username>/lecturerhub`
  - Working directory: `/home/<username>/lecturerhub`
- **WSGI configuration file**: click the link to edit it, delete the
  boilerplate, and replace with:

```python
import os
import sys

path = '/home/<username>/lecturerhub'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

(`config.settings.prod` requires `DJANGO_ALLOWED_HOSTS` to be set — that's
the `.env` value from step 3 — and forces HTTPS redirects/secure cookies,
which is correct since PythonAnywhere serves `*.pythonanywhere.com` over
HTTPS by default.)

## 5. Static and media file mappings

Still on the **Web** tab, under **Static files**, add two mappings:

| URL | Directory |
|---|---|
| `/static/` | `/home/<username>/lecturerhub/staticfiles` |
| `/media/` | `/home/<username>/lecturerhub/media` |

Then, back in the Bash console (with the virtualenv active):
```bash
workon lecturerhub-venv
cd ~/lecturerhub
python manage.py collectstatic --noinput
```

## 6. Migrate and create your account

```bash
python manage.py migrate
python manage.py create_default_user
python manage.py seed_demo   # optional
```

## 7. Reload

Back on the **Web** tab, click the big green **Reload** button, then visit
`https://<your-username>.pythonanywhere.com/`.

## Updating after a git push

```bash
workon lecturerhub-venv
cd ~/lecturerhub
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
Then hit **Reload** on the Web tab again — PythonAnywhere doesn't
auto-restart on file changes like `runserver` does locally.

## Notes specific to PythonAnywhere

- **No gunicorn/nginx needed** — PythonAnywhere runs your WSGI app directly
  under their own uWSGI-based infrastructure via the WSGI file above.
- **Free tier** restricts outbound internet access to an allowlist. The DOI
  import feature calls `api.crossref.org` — on a free account you'll need
  to add `api.crossref.org` to the allowlist (Account → "Add a new
  allowed domain") or it will fail with a connection error; paid accounts
  have unrestricted outbound access.
- **Scheduled tasks**: PythonAnywhere's free tier includes one daily
  scheduled task slot if you ever want to automate anything (not required
  for this app — everything here is triggered by page requests).
