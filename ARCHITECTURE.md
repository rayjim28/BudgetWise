# BudgetWise V2 — Architecture

The V2 redesign keeps **Django and the current database schema**. Do not rewrite
budget or expense records or switch to a frontend framework just for styling.

```text
budgetwise-v2/
├── frontend/
│   ├── templates/               # Django templates for all current pages
│   └── static/
│       ├── css/style.css        # Original shared UI styles
│       ├── css/dashboard-v2.css # New dark visual theme
│       └── js/app.js            # Mobile navigation behavior
├── middleware/
│   └── privacy.py               # Privacy policy response headers
├── backend/
│   └── main_app/
│       ├── models.py            # Existing DB models (unchanged)
│       ├── migrations/          # All original migrations (unchanged)
│       ├── views.py             # Original business logic (unchanged)
│       ├── forms.py
│       ├── urls.py
│       └── tests.py             # Existing integration tests
├── budgetmanager/               # Django configuration, WSGI, ASGI
├── manage.py
├── build.sh
└── requirements.txt
```

**Why the Django app keeps the label `main_app`:** its Python import path changes
to `backend.main_app`, but `MainAppConfig.label` remains `main_app`. This keeps
Django's existing database table names, migration identity, and relationships.

## Safe local review

Run in a new clone or worktree, never directly against production. Do not copy
production `DATABASE_URL` or `.env` into the redesign checkout. The Git repo may
contain a tracked `db.sqlite3`: don't edit or commit it.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
DJANGO_DEBUG=true python manage.py check
DJANGO_DEBUG=true python manage.py test
DJANGO_DEBUG=true python manage.py makemigrations --check --dry-run
```

For local visual testing, use a **new** SQLite database file, not `db.sqlite3`:

```bash
export DJANGO_DEBUG=true
export DATABASE_URL=sqlite:///local-v2.sqlite3
python manage.py migrate
python manage.py runserver
```

`local-v2.sqlite3` matches `.gitignore`'s `*.sqlite3` rule.
Create a local account at `/signup/`; once signed in, view `/dashboard/`.
The local database is for testing only, not a source of production records.

Optional: after creating an account in this **isolated local V2 database**, you can
populate it with illustrative chart data:

```bash
python manage.py seed_demo --username YOUR_LOCAL_ACCOUNT_USERNAME
```

This refuses to run against PostgreSQL, a non-local-V2 SQLite file, a non-DEBUG
server, or an account that already contains records. It never runs automatically.
The sample values are not your finances and are not used in production.

## Deploying

Deployment stays `./build.sh` with `gunicorn budgetmanager.wsgi:application`.
Django static files are now discovered in `frontend/static/` and gathered by
`collectstatic`. Keep existing environment variables and secrets on Render.
Do not merge or deploy until Django checks, test suite, login, budgets,
transactions, reports, CSV, and static file serving have been verified.

The dashboard's six-month chart is based on **dated expenses**. Existing income
records have no date column, so no fabricated income-by-month chart is shown.
