# Architecture

LecturerHub is a single-user Django 5 application. "Single-user" only means
the UI and seed data assume one lecturer owns all records — the auth system
is Django's standard `User`/session model, so a second account can be added
later (e.g. for a co-supervisor) without any schema changes.

## App layout

```
lecturerhub/
├── manage.py
├── config/                  settings, root urls, wsgi/asgi
│   └── settings/
│       ├── base.py          shared settings, reads .env
│       ├── dev.py           DEBUG=True, ALLOWED_HOSTS=["*"]
│       └── prod.py          security headers, requires DJANGO_ALLOWED_HOSTS
├── apps/
│   ├── accounts/            Profile (1:1 with User), login/profile views
│   ├── cv/                  Education, Position, Achievement, Skill,
│   │                        TrainingCertification, CV PDF export
│   ├── documents/           Document vault (SK, certificates, LoA, ...)
│   ├── publications/        Publication, IntellectualProperty, DOI import
│   ├── schedule/             Semester, Course, TeachingAssignment, Event,
│   │                        calendar views, ICS export
│   ├── supervision/         Student, Milestone, SupervisionLog
│   ├── research/            Grant, Deliverable
│   ├── service/             CommunityService, OrganizationalRole
│   ├── dashboard/           Home aggregation view, global search,
│   │                        public pages (public_views.py), seed_demo
│   └── common/               Shared HTMX helpers + the generic
│                            public/private toggle used across apps
├── templates/                One directory per app, plus templates/base.html
│                            (authenticated shell) and templates/public/
│                            (the public-page shell, used with no login)
├── static/
├── tests/                    All pytest tests (flat, not per-app)
└── docs/                      This folder
```

## Why each app exists

- **accounts** — holds the `Profile` model (the lecturer's personal/contact
  data) separately from Django's built-in `User`, so `User` stays a pure auth
  record and `Profile` can carry public-page fields (`public_slug`,
  `public_email`, `show_phone_publicly`) without touching auth internals.
- **documents** — a flat file vault referenced by FK from `cv.Position`
  (SK), `cv.Achievement`/`cv.TrainingCertification` (certificates),
  `publications.IntellectualProperty` (DJKI certificate), and
  `research.Deliverable`. It has no `is_public` field — documents are never
  shown on public pages, only linked from records that are.
- **cv** — the "traditional CV" data: education, positions, achievements,
  skills, training. Also owns the two PDF export code paths
  (`pdf_academic.py`, `pdf_europass.py`) and `pdf_data.py`, the single
  function (`get_cv_context`) that both the PDF exporters and the public CV
  page pull from, so the two never drift apart.
- **publications** — `Publication` and `IntellectualProperty`, plus a
  CrossRef-backed DOI import helper (`crossref.py`) so adding a journal
  article doesn't mean retyping its metadata.
- **schedule** — the only app with a genuinely recurring concept
  (`TeachingAssignment` repeats weekly for a `Semester`). Calendar rendering
  and the `.ics` export (`ics_export.py`) both expand that recurrence into
  concrete occurrences; the ICS file additionally expresses it as an
  `RRULE` for calendar apps to expand themselves.
- **supervision** — thesis students. Kept separate from `cv` because its
  data (milestones, meeting logs) is operational, not resume material, and
  because the per-student timeline view is a distinct workflow from CRUD.
- **research** — grants and their deliverables. `Grant` was actually
  introduced early (Phase 3) because `Publication.grant` is an FK to it —
  see the git history if the phase numbering looks odd.
- **service** — community service (pengabdian) and organizational roles.
  Small and self-contained; split from `cv` only because the master spec
  grouped them separately in the sidebar.
- **dashboard** — has no models of its own. It's the aggregation layer
  (`views.py: home`), the global search (`views.py: search`), the two
  public routes (`public_views.py`), and `seed_demo`.
- **common** — not a Django "content" app (no models), just shared code:
  the HTMX toast-header helper (`htmx.py`) every app's delete views use, and
  the generic public/private toggle (`views.py`) that all 11 `is_public`
  models share via an explicit model allowlist rather than 11 near-identical
  views.

## Request flow

A typical authenticated CRUD request:

1. `config/urls.py` routes `/cv/education/3/edit/` to
   `apps.cv.urls` → `EducationUpdateView`.
2. `LoginRequiredMixin` redirects to `/login/` if unauthenticated.
3. The view renders `templates/cv/education_form.html`, which extends
   `templates/base.html` — the authenticated shell (sidebar + navbar
   search + toast container).
4. On POST, `ToastFormMixin.form_valid` saves the form and adds a Django
   message; the redirect target re-renders the list page, which shows the
   message as a banner.
5. Row deletes go through a shared `HtmxDeleteView.post`: an HTMX request
   gets a 200 with an empty body plus an `HX-Trigger` header carrying the
   toast payload (`apps/common/htmx.py`), so the row disappears in place
   without a full page reload; a non-HTMX POST redirects normally.

A public-page request (`/p/cv/` or `/p/cv/<slug>/`):

1. `apps.dashboard.public_urls` routes to `public_views.public_cv`, which
   is **not** behind `LoginRequiredMixin` — there is no auth check at all.
2. The view enforces `PUBLIC_PAGES_MODE` itself (not via URL registration):
   in `"unlisted"` mode it 404s unless the slug in the URL matches
   `Profile.public_slug`; in `"open"` mode the slug is ignored.
3. `get_cv_context(public_only=True)` is fetched from the cache
   (`public_cv_context`, 5-minute TTL) or built and cached on a miss —
   built with every queryset realized to a list first, so a cache hit
   skips the database entirely rather than just re-deriving a lazy
   queryset.
4. The template extends `templates/public/_base.html`, a minimal shell
   with no sidebar and no auth branching — this exists specifically so
   that an authenticated owner previewing their own public page still
   sees the public layout, not the authenticated one.
5. In `"unlisted"` mode the response gets `X-Robots-Tag: noindex`.

## Shared conventions

- Every list-with-CRUD app follows the same view shape: a `ListView`, plain
  `CreateView`/`UpdateView` mixed with a local `ToastFormMixin`, and a
  `DeleteView` subclassing a local `HtmxDeleteView`. This is duplicated
  per-app rather than pulled into one base class in `apps/common` — an
  intentional trade-off made early in the build; consolidating it is a
  reasonable follow-up if the pattern needs to change in one place.
- Every `is_public`-bearing model is CRUD'd through the same generic
  toggle in `apps/common/views.py`, gated by an explicit
  `ALLOWED_PUBLIC_TOGGLE_MODELS` set — adding a new public-facing model
  means adding one line there and one `{% include %}` in its list
  template, not a new view.
