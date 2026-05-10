import os
from pathlib import Path
from urllib.parse import urlsplit

BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file():
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()


def csv_env(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def env_value(name, default=""):
    return os.getenv(name, default).strip().strip('"').strip("'")


def normalize_allowed_host(value):
    host = value.strip()
    if "://" in host:
        host = urlsplit(host).netloc
    return host.split("/")[0]


def normalize_csrf_origin(value):
    origin = value.strip().rstrip("/")
    if not origin:
        return ""
    if "://" not in origin:
        origin = f"https://{origin}"
    parsed = urlsplit(origin)
    return f"{parsed.scheme}://{parsed.netloc}"


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    host
    for host in (normalize_allowed_host(item) for item in csv_env("ALLOWED_HOSTS", "127.0.0.1,localhost,drivedesk.onrender.com"))
    if host
]
CSRF_TRUSTED_ORIGINS = [
    origin
    for origin in (normalize_csrf_origin(item) for item in csv_env("CSRF_TRUSTED_ORIGINS", "https://drivedesk.onrender.com"))
    if origin
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", str(not DEBUG)).lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", str(not DEBUG)).lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", str(not DEBUG)).lower() == "true"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "showcase",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "luxe_mindset.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "luxe_mindset.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@drivedesk.local")
ORDER_NOTIFICATION_EMAIL = "temp@gmail.com"

SITE_URL = env_value("SITE_URL", "http://127.0.0.1:8000").rstrip("/")
STRIPE_PUBLISHABLE_KEY = env_value(
    "STRIPE_PUBLISHABLE_KEY",
    "pk_live_51TVLlz2W3YUSIAQzxWnyx2Z3R79CHA4wKDdtn08DyGYtkEWk7Nj6F9AbhQly3BXmJarvUrGAbC4llPdmTt660V9S00d4h3pwx5",
)
STRIPE_SECRET_KEY = env_value("STRIPE_SECRET_KEY")
PAYPAL_CLIENT_ID = env_value("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = env_value("PAYPAL_CLIENT_SECRET")
PAYPAL_API_BASE = env_value("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com").rstrip("/")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
