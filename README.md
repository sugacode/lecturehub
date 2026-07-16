# LecturerHub

A personal management system for an Indonesian university lecturer: teaching
schedule, thesis supervision, publications (with DOI import), research
grants, community service, a document vault, and a CV that exports to PDF
in two styles — plus an interactive public CV/schedule page you can share.

Built with Django 5, Django templates + Tailwind (CDN, no Node build step),
HTMX, Alpine.js, and ReportLab for PDF generation. Single-user today, but
built on Django's standard auth system so a second account can be added
later without schema changes.

## Quick start (macOS)

```bash
git clone <repo-url> lecturerhub && cd lecturerhub
/opt/homebrew/bin/python3.12 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip && pip install -r requirements.txt
cp .env.example .env   # then edit DJANGO_SECRET_KEY and DEFAULT_ADMIN_*
python manage.py migrate
python manage.py create_default_user
python manage.py seed_demo   # optional: populate demo data
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and log in with the `DEFAULT_ADMIN_*`
credentials from your `.env`. There is no signup page — `create_default_user`
is the only way to create an account.

Full step-by-step instructions (Python install, venv, editor setup,
switching to PostgreSQL) are in [`docs/SETUP_MACOS.md`](docs/SETUP_MACOS.md).

## Documentation

| Doc | Covers |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | App layout, why each app exists, request flow |
| [`docs/DATABASE.md`](docs/DATABASE.md) | Every model and field, plus a Mermaid ER diagram |
| [`docs/SETUP_MACOS.md`](docs/SETUP_MACOS.md) | Full local setup, VS Code / PyCharm, PostgreSQL migration |
| [`docs/API_INTERNALS.md`](docs/API_INTERNALS.md) | Full URL map, management commands, env vars |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | How to use every feature, written for the lecturer |

## Running tests and linting

```bash
pytest                  # 121+ tests
ruff check .             # lint (line length 100)
python manage.py check   # Django system checks
```

## Key features

- **CRUD everywhere** via Django class-based views, with HTMX inline row
  deletes (confirm dialog + toast, no full page reload) on every list page.
- **CV export**: `/cv/export/?style=academic` or `?style=europass`,
  generated with ReportLab from live data — nothing to fill in twice.
- **DOI import**: paste a DOI on the Publications page, metadata is fetched
  from CrossRef and prefills the add-publication form.
- **ICS export**: `/schedule/export.ics` — subscribe from Apple Calendar to
  keep your teaching schedule and events synced.
- **Global search**: one box in the navbar, searches publications,
  students, documents, and events at once.
- **Public pages**: `/p/cv/` (interactive, with client-side publication
  filters) and `/p/schedule/` (read-only weekly calendar), both showing
  only records you've explicitly marked public. `PUBLIC_PAGES_MODE=open`
  serves them directly; `unlisted` requires a private slug and sets
  `X-Robots-Tag: noindex`.
- **Privacy controls**: a public/private toggle on every relevant list row,
  plus a bulk "make public" action.

## Project layout

```
apps/            One Django app per feature area (accounts, cv, documents,
                  publications, schedule, supervision, research, service,
                  dashboard, common)
config/           Settings (base/dev/prod), root urls
templates/        One directory per app, plus the shared base.html and
                  public/ (the no-auth public-page shell)
tests/            All pytest tests
docs/             Architecture, database, setup, internals, user guide
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown
and why each app exists.
