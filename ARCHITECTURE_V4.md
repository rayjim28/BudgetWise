# BudgetWise V4 — application architecture

The app remains Django. Separate folders define responsibilities without rewriting its persistence or introducing a second frontend framework.

```text
budgetwise-v2/
├── frontend/
│   ├── templates/                  # Django pages: dashboard, budgets, forms, reports, accounts
│   └── static/
│       ├── css/                   # Base styles + V2/V3/V4 dashboard refinements
│       └── js/                    # Navigation and interaction
├── middleware/
│   └── privacy.py                 # Privacy response headers
├── backend/
│   └── main_app/
│       ├── views/
│       │   ├── common.py          # User-scoped data access and shared totals
│       │   ├── public.py          # Landing, about, signup
│       │   ├── dashboard.py       # Dashboard metrics and expense comparisons
│       │   ├── budgets.py         # Budget CRUD
│       │   ├── incomes.py         # Income CRUD
│       │   ├── expenses.py        # Expense CRUD
│       │   ├── transactions.py    # Transaction browsing and CSV export
│       │   ├── reports.py         # Financial reports
│       │   └── __init__.py        # Existing Django view exports
│       ├── urls.py                # Existing URL names and patterns
│       ├── forms.py               # Validated input forms
│       ├── models.py              # Original database models, unchanged
│       ├── migrations/            # Original migrations, unchanged
│       └── tests.py               # Integration and ownership tests
├── budgetmanager/                 # Django project settings, WSGI and ASGI entrypoints
├── manage.py
├── build.sh
└── requirements.txt
```

The `backend.main_app.apps.MainAppConfig` app uses `label = 'main_app'`, which retains historical database table names and migration identity. Built-in Django auth, session, and CSRF middleware remain in the `budgetmanager.settings` middleware list; `middleware/privacy.py` is the app's custom request/response middleware.

**Deployment contract:** `./build.sh` and `gunicorn budgetmanager.wsgi:application` stay unchanged. In Render, configure `DATABASE_URL`, `DJANGO_SECRET_KEY`, allowed hosts, and trusted CSRF origins. Verify the service is configured for PostgreSQL and has a database backup before promoting this branch to `main`.

**Important:** historical `Income` rows do not include dates. The 12-month comparison therefore uses recorded expenses from the current and preceding year, not invented income history.
