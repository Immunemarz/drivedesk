# DriveDesk Supply

A premium Django storefront concept for curated productivity gear and car accessory bundles.

## Run locally

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

## Deploy on Render

Install dependencies and collect static files during the Render build:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Use this start command:

```bash
gunicorn luxe_mindset.wsgi:application
```

Set production environment variables in Render:

```text
DEBUG=false
ALLOWED_HOSTS=drivedesk.onrender.com
CSRF_TRUSTED_ORIGINS=https://drivedesk.onrender.com
SITE_URL=https://drivedesk.onrender.com
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
```

## Environment variables

The app reads secrets and payment settings from `.env` in the project root.

Important keys:

```text
DJANGO_SECRET_KEY=
EMAIL_HOST=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_API_BASE=https://api-m.paypal.com
```

Use `.env.example` as the template and keep `.env` local.

For live Stripe checkout, use:

```text
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
```

The publishable key can be visible in browser-side Stripe setup, but the secret key must only live in `.env` locally or in Render environment variables.

On Windows PowerShell, if your virtual environment uses `Scripts` instead of `bin`, run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver
```
