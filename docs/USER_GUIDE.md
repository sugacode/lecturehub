# User Guide

This guide walks through using LecturerHub day to day. It assumes you've
already followed `docs/SETUP_MACOS.md` and can log in.

## Getting around

The sidebar (collapses to a top menu on mobile) has one section per area of
your academic life: **Dashboard, Schedule, Supervision, Publications,
Research, CV, Service, Documents, Profile**. The search box in the top bar
searches across publications, students, documents, and events at once —
type a few characters and press Enter to see grouped results.

Dark mode toggles from the sidebar and is remembered across visits (stored
in a cookie, not tied to your account).

## Dashboard

Your home page. Four stat cards (publications, active grants, active
students, documents expiring soon) plus two lists: what's happening in the
**next 7 days** (merging your teaching schedule and calendar events), and
what's **due within 30 days** (research deliverables and thesis
milestones). Nothing here needs manual refreshing — it's always computed
from today's date.

## Schedule

- **Week view** (the default) shows Monday–Saturday, merging your active
  semester's recurring teaching with one-off events. Use the "Previous
  week" / "Next week" links to look ahead or back.
- **Month view** is events only, laid out on a standard calendar grid.
- **Semesters / Courses / Assignments** are where you set up the recurring
  weekly pattern: create a Semester, mark it active, add Courses, then
  create Teaching Assignments linking a course to a semester with a
  day/time/room. Only one semester should be active at a time — the week
  view and the public schedule both key off whichever one is.
- **Events** cover anything one-off: meetings, seminars, deadlines,
  personal blocks. Each event has a **Visibility** dropdown right in the
  list — *Private* (only you see it), *Busy* (shows as an untitled "Busy"
  block on your public schedule), or *Public* (shows its title and
  location publicly, never its notes or meeting link).
- **Export .ics**: click "Export .ics" from any schedule page to download
  a calendar file. Subscribe to it from Apple Calendar (File → New
  Calendar Subscription) to keep your teaching schedule and events synced
  without re-entering them.

## Supervision

The student list shows an "Overdue milestones" count per student, so you
can see at a glance who needs attention. Click a student's name to open
their **timeline** — a single page merging every milestone and supervision
log, newest first, with inline forms to add another milestone or log a
meeting without leaving the page.

## Publications

Add publications by hand, or click **Import from DOI**: paste a DOI (e.g.
`10.1371/journal.pone.0000308`), and it fetches the title, authors, venue,
year, volume/issue/pages, and citation count from CrossRef, prefilling the
add-publication form for you to review and save. If CrossRef is
unreachable you'll get a plain error message instead of a crash — just try
again or enter the details manually.

The **Intellectual Property** tab (same section) tracks DJKI-registered
copyrights, patents, and trademarks.

## Research

Grants show role (PI/Co-PI/Member), status, and funding period. Click a
grant's title to open its detail page, where you can add and track
**Deliverables** (reports, publications, prototypes, IP) with due dates and
a completed checkbox.

## CV

Five tabs — Education, Positions, Achievements, Skills, Training — plus
two buttons in the same nav bar: **Export PDF (Academic)** and **Export PDF
(Europass)**. Both pull directly from whatever you've entered across the
whole app (education, positions, publications, grants, supervision counts,
service, achievements, skills) — there's nothing separate to fill in for
the CV itself. The Academic style groups publications by type with numbered
citations; the Europass style uses the conventional dates-in-a-left-column
layout.

## Service

**Community Service** (pengabdian kepada masyarakat) and **Organizational
Roles** (e.g. ICMI, APSI PTMA membership) are separate tabs in the same
section.

## Documents

A flat file vault for SKs, certificates, letters of appointment, contracts,
and reports. Filter by category or search by title/tag. Other sections
(Positions, Achievements, Training, Intellectual Property, Deliverables)
can link to a document here as supporting evidence — upload it once in
Documents, then pick it from the dropdown when editing that record.

## Profile

Your personal and contact details, including IDs (NIDN, NIP, ORCID,
Scopus, SINTA, Google Scholar) used across the CV and publications. Two
fields specifically control what the public CV shows instead of your real
contact details: **Public email** (leave blank to show no email publicly)
and **Show phone publicly** (a checkbox — off by default).

The **Public pages** box at the bottom shows direct links to your public
CV and public schedule, plus a **Regenerate public link** button. That
button only matters if your server is running in "unlisted" mode (an admin
/ deployment setting, not something you toggle here) — regenerating
invalidates the old link immediately, so use it if you think the link was
shared somewhere you didn't intend.

## Making records public

Every record type that can appear on your public CV (education, positions,
achievements, skills, training, publications, intellectual property,
grants, community service, organizational roles, teaching assignments) has
a **Public** / **Private** badge in its list page — click it to flip that
one record. To flip several at once: tick their checkboxes and click "Make
selected public" above the table (there's no bulk "make private" — flip
those back individually).

Nothing is public by default. A record only shows up on `/p/cv/` or
`/p/schedule/` once you've explicitly marked it public.

## Public pages

`/p/cv/` is what anyone with the link sees: your profile header, an
anchored section nav, and — only for publications — three dropdown filters
(type, year, indexing) that narrow the list instantly without reloading
the page. A "Download PDF" button there generates the same Academic-style
PDF, filtered to public records only.

`/p/schedule/` is a read-only weekly view of your public teaching slots
and public/busy events — no student counts, no meeting links, no notes,
ever.
