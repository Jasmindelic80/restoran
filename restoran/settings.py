from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Core env settings
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Render ti daje domen npr. xxxx.onrender.com
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(",") if h.strip()]

# CSRF (preporučeno za Render HTTPS)
CSRF_TRUSTED_ORIGINS = []
csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins.split(",") if o.strip()]

# =========================
# Apps
# =========================
INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",

    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # tvoje aplikacije
    "korisnici",
    "meni",
    "stolovi",
    "narudzba.apps.NarudzbaConfig",
    "lager",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "restoran.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "restoran.wsgi.application"

# =========================
# Database
# =========================
# Render: koristi DATABASE_URL (Postgres)
# Lokalno: ako DATABASE_URL ne postoji -> SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# =========================
# Password validation
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# =========================
# Static files (Render)
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Ako imaš local static folder:
STATICFILES_DIRS = []
static_dir = BASE_DIR / "static"
if static_dir.exists():
    STATICFILES_DIRS = [static_dir]

# WhiteNoise storage
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# Auth redirects (ostavi ako ti treba)
# =========================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# =========================
# CORS
# =========================
CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True").lower() == "true"

# =========================
# DRF
# =========================
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Basic auth ti je ok ako koristiš klijent (npr. Tkinter)
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
}

from django.contrib.auth import get_user_model
import os

if os.getenv("CREATE_SUPERUSER") == "True":
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )
