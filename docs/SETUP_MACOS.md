# macOS Setup

## 1. Install Python 3.12

The project targets Python 3.12. Check what you have first:

```bash
python3 --version
```

If it's not 3.12.x, install it with Homebrew (recommended) or pyenv.

**Homebrew:**
```bash
brew install python@3.12
```
This installs the interpreter at `/opt/homebrew/bin/python3.12` without
touching your system Python.

**pyenv (if you manage multiple Python versions):**
```bash
brew install pyenv
pyenv install 3.12
pyenv local 3.12  # run inside the project directory
```

## 2. Clone and create a virtual environment

```bash
git clone <repo-url> lecturerhub
cd lecturerhub
/opt/homebrew/bin/python3.12 -m venv .venv
source .venv/bin/activate
```

Your shell prompt should now show `(.venv)`. Every command below assumes
the virtualenv is active — if you open a new terminal tab, re-run
`source .venv/bin/activate` first.

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```
DJANGO_SECRET_KEY=<any random string — python -c "import secrets; print(secrets.token_urlsafe(50))">
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_EMAIL=you@example.com
DEFAULT_ADMIN_PASSWORD=<a real password>
```

Leave `DATABASE_URL` unset to use SQLite (the default for local dev — see
"Switching to PostgreSQL" below). Leave `PUBLIC_PAGES_MODE=open` unless you
specifically want the unlisted-slug behavior (see `docs/API_INTERNALS.md`).

## 5. Migrate and create your account

```bash
python manage.py migrate
python manage.py create_default_user
```

`create_default_user` reads `DEFAULT_ADMIN_*` from `.env` and creates (or
updates) that one account. There is no signup page — this command is the
only way to create a user.

## 6. Seed demo data (optional but recommended)

```bash
python manage.py seed_demo
```

Creates a semester, three courses, five publications, two grants, three
supervised students, and a handful of events, so the dashboard and list
pages aren't empty on first run. Safe to run more than once — it uses
`get_or_create` and won't duplicate records.

## 7. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and log in with the `DEFAULT_ADMIN_*`
credentials from your `.env`.

## Opening the project in an editor

**VS Code:**
1. `code .` from the project root.
2. Install the "Python" extension (Microsoft) if you don't have it.
3. Cmd+Shift+P → "Python: Select Interpreter" → pick `.venv/bin/python`.
4. Recommended extensions: Python (ms-python.python), Pylance
   (ms-python.vscode-pylance), Django (batisteo.vscode-django) for
   template syntax highlighting, Tailwind CSS IntelliSense
   (bradlc.vscode-tailwindcss).

**PyCharm / WebStorm (JetBrains):**
1. Open the project folder.
2. Settings → Project → Python Interpreter → Add Interpreter → Existing
   environment → point at `.venv/bin/python`.
3. PyCharm Professional detects Django projects automatically and offers a
   Django-aware run configuration; Community Edition works fine too, just
   without the template debugger.
4. Since this project has no `package.json` / Node build step, WebStorm
   isn't the natural fit here — PyCharm (or VS Code) is recommended.

## Running tests and linting

```bash
pytest                # runs the full suite (tests/)
ruff check .           # lint
python manage.py check # Django system checks
```

## Switching to PostgreSQL later

The settings already support it via `dj-database-url` — nothing in the
codebase needs to change, only `.env`:

```bash
brew install postgresql@16
brew services start postgresql@16
createdb lecturerhub
```

Then in `.env`:
```
DATABASE_URL=postgres://localhost:5432/lecturerhub
```

Re-run `python manage.py migrate` against the new database, then
`create_default_user` and (optionally) `seed_demo` again — they don't
carry over from SQLite automatically.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'django'`** — the virtualenv
  isn't active. Run `source .venv/bin/activate`.
- **`django.core.exceptions.ImproperlyConfigured: ... DJANGO_ALLOWED_HOSTS`**
  — this only happens under `config.settings.prod`; local dev uses
  `config.settings.dev` (the default in `manage.py`), which doesn't
  require it.
- **Port 8000 already in use** — `python manage.py runserver 8001` and
  visit that port instead.
- **Uploaded files (photos, documents) not showing** — confirm
  `MEDIA_ROOT`/`media/` exists and is writable; `manage.py runserver`
  serves media automatically when `DEBUG=True`.
