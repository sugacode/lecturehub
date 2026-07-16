# Internals reference

This isn't a REST API — LecturerHub is server-rendered Django templates
plus HTMX for partial updates. "API_INTERNALS" here means: every URL, every
management command, and every environment variable, in one place.

## URL map

All authenticated routes require login (redirect to `/login/`) except the
two marked **public**. `<int:pk>` etc. are Django path converters.

### Auth
| URL | Name |
|---|---|
| `/login/` | `login` |
| `/logout/` | `logout` |

### accounts
| URL | Name |
|---|---|
| `/accounts/profile/` | `accounts:profile_edit` |
| `/accounts/profile/regenerate-slug/` | `accounts:regenerate_slug` |

### dashboard
| URL | Name |
|---|---|
| `/` | `dashboard:home` |
| `/search/` | `dashboard:search` |

### cv
| URL | Name |
|---|---|
| `/cv/export/` | `cv:export` — **public**, see "Public pages" below |
| `/cv/` | `cv:education_list` |
| `/cv/education/new/` `/cv/education/<pk>/edit/` `/cv/education/<pk>/delete/` | `cv:education_create` / `education_update` / `education_delete` |
| `/cv/positions/` (+ `new/`, `<pk>/edit/`, `<pk>/delete/`) | `cv:position_*` |
| `/cv/achievements/` (+ ...) | `cv:achievement_*` |
| `/cv/skills/` (+ ...) | `cv:skill_*` |
| `/cv/training/` (+ ...) | `cv:training_*` |

### publications
| URL | Name |
|---|---|
| `/publications/` | `publications:publication_list` |
| `/publications/new/`, `<pk>/edit/`, `<pk>/delete/` | `publications:publication_create` / `_update` / `_delete` |
| `/publications/import/` | `publications:import_by_doi` |
| `/publications/ip/` (+ `new/`, `<pk>/edit/`, `<pk>/delete/`) | `publications:ip_*` |

### schedule
| URL | Name |
|---|---|
| `/schedule/` | `schedule:calendar_week` |
| `/schedule/month/` | `schedule:calendar_month` |
| `/schedule/export.ics` | `schedule:export_ics` |
| `/schedule/semesters/` (+ ...) | `schedule:semester_*` |
| `/schedule/courses/` (+ ...) | `schedule:course_*` |
| `/schedule/assignments/` (+ ...) | `schedule:assignment_*` |
| `/schedule/events/` (+ ...) | `schedule:event_*` |
| `/schedule/events/<pk>/visibility/` | `schedule:event_set_visibility` (HTMX PATCH-style) |

### supervision
| URL | Name |
|---|---|
| `/supervision/` | `supervision:student_list` |
| `/supervision/new/`, `<pk>/edit/`, `<pk>/delete/` | `supervision:student_create` / `_update` / `_delete` |
| `/supervision/<pk>/` | `supervision:student_timeline` |
| `/supervision/<student_pk>/milestones/new/` | `supervision:milestone_create` |
| `/supervision/milestones/<pk>/delete/` | `supervision:milestone_delete` |
| `/supervision/<student_pk>/logs/new/` | `supervision:log_create` |
| `/supervision/logs/<pk>/delete/` | `supervision:log_delete` |

### research
| URL | Name |
|---|---|
| `/research/` | `research:grant_list` |
| `/research/new/`, `<pk>/edit/`, `<pk>/delete/` | `research:grant_create` / `_update` / `_delete` |
| `/research/<pk>/` | `research:grant_detail` |
| `/research/<grant_pk>/deliverables/new/` | `research:deliverable_create` |
| `/research/deliverables/<pk>/edit/`, `<pk>/delete/` | `research:deliverable_update` / `_delete` |

### service
| URL | Name |
|---|---|
| `/service/` | `service:community_service_list` |
| `/service/new/`, `<pk>/edit/`, `<pk>/delete/` | `service:community_service_*` |
| `/service/roles/` (+ ...) | `service:organizational_role_*` |

### documents
| URL | Name |
|---|---|
| `/documents/` | `documents:document_list` |
| `/documents/new/`, `<pk>/edit/`, `<pk>/delete/` | `documents:document_create` / `_update` / `_delete` |

### common (shared HTMX toggles)
| URL | Name |
|---|---|
| `/common/toggle-public/<app_label>/<model_name>/<pk>/` | `common:toggle_public` |
| `/common/bulk-make-public/<app_label>/<model_name>/` | `common:bulk_make_public` |

`app_label`/`model_name` are restricted to an explicit allowlist in
`apps/common/views.py` (`ALLOWED_PUBLIC_TOGGLE_MODELS`); any other pair 404s.

### Public pages
| URL | Name | Notes |
|---|---|---|
| `/p/cv/` | `public:public_cv` | 404s if `PUBLIC_PAGES_MODE=unlisted` |
| `/p/cv/<slug>/` | `public:public_cv_slug` | slug must match `Profile.public_slug` |
| `/p/schedule/` | `public:public_schedule` | 404s if `PUBLIC_PAGES_MODE=unlisted` |
| `/p/schedule/<slug>/` | `public:public_schedule_slug` | slug must match `Profile.public_slug` |
| `/cv/export/` | `cv:export` | public; `?style=academic\|europass`; add `?slug=<public_slug>` when unlisted |

### Django admin
`/admin/` — standard Django admin, every model registered. Never linked
from any public page.

## Management commands

| Command | Purpose |
|---|---|
| `create_default_user` | Creates or updates the single admin account from `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD`. No signup page exists — this is the only way to create a user. |
| `seed_demo` | Idempotently creates one semester, three courses, five publications, two grants, three students (with a milestone and a log each), four events, and a handful of supporting CV/service records. |

Both are plain `manage.py` subcommands: `python manage.py create_default_user`.

## Environment variables

Defined in `.env` (copy from `.env.example`), read by `config/settings/base.py`
via `python-dotenv`.

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure placeholder | Django's `SECRET_KEY`. Set a real value outside local dev. |
| `DJANGO_DEBUG` | `False` | `DEBUG`. `config.settings.dev` forces `True` regardless. |
| `DJANGO_ALLOWED_HOSTS` | empty | Comma-separated hosts. Required (non-empty) under `config.settings.prod`. |
| `DATABASE_URL` | unset → SQLite at `BASE_DIR/db.sqlite3` | Any `dj-database-url`-parseable URL, e.g. `postgres://user:pass@host:5432/db`. |
| `PUBLIC_PAGES_MODE` | `open` | `open` serves `/p/cv/` and `/p/schedule/` directly. `unlisted` 404s those and only serves the `<slug>` variants, with `X-Robots-Tag: noindex`. |
| `DEFAULT_ADMIN_USERNAME` | — | Used only by `create_default_user`. |
| `DEFAULT_ADMIN_EMAIL` | — | Used only by `create_default_user`. |
| `DEFAULT_ADMIN_PASSWORD` | — | Used only by `create_default_user`. |

## HTMX conventions used throughout

- **Row delete**: buttons use `hx-post` (not `hx-delete` — simpler CSRF
  handling) to a `<model>_delete` URL, `hx-target` the row, `hx-swap`
  `outerHTML`, and `hx-confirm` for the browser-native confirmation dialog.
  The view responds with an empty 200 body and an `HX-Trigger` header
  carrying `{"toast": {"message": ..., "level": ...}}`, which
  `templates/base.html`'s Alpine `toaster` component listens for on
  `document.body` and renders as a floating toast.
- **Public/private toggle**: `templates/common/_public_toggle.html` is an
  `hx-post` button to `common:toggle_public` that swaps itself
  (`hx-swap="outerHTML"`) with the server-rendered updated badge.
- **CSRF for HTMX**: `templates/base.html` registers a global
  `htmx:configRequest` listener that reads the `csrftoken` cookie and adds
  it as an `X-CSRFToken` header to every HTMX request; a page-wide
  `{% csrf_token %}` tag (outside any form) guarantees the cookie is always
  set, even on pages with no visible form.
