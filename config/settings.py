"""
Django settings for config project.
"""

import os
from pathlib import Path

import dj_database_url


# ============================================================
# CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SEGURANÇA
# ============================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-chave-apenas-para-desenvolvimento-local",
)

DEBUG = os.environ.get("DEBUG", "True").lower() == "true"


ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


# No Render, adiciona automaticamente o endereço
# disponibilizado pelo próprio serviço.
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if RENDER_EXTERNAL_HOSTNAME:
    if RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ============================================================
# APLICAÇÕES
# ============================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "estoque",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise permite que o próprio Django/Render
    # entregue os arquivos estáticos em produção.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URLS
# ============================================================

ROOT_URLCONF = "config.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
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


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "config.wsgi.application"


# ============================================================
# BANCO DE DADOS
# ============================================================
#
# LOCAL:
#   Sem DATABASE_URL -> SQLite.
#
# ONLINE:
#   Com DATABASE_URL -> PostgreSQL.
#
# Isso permite continuar trabalhando normalmente no computador
# e usar PostgreSQL quando o projeto estiver no Render.
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")


if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# VALIDAÇÃO DE SENHAS
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNACIONALIZAÇÃO
# ============================================================

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# ============================================================
# ARQUIVOS ESTÁTICOS
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# Django 6.1 / WhiteNoise
#
# O WhiteNoise usa ManifestStaticFilesStorage para gerar
# arquivos estáticos com nomes versionados.
#
# Isso é importante para o funcionamento correto em produção.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ============================================================
# ARQUIVOS DE MÍDIA
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# E-MAIL
# ============================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ============================================================
# AUTENTICAÇÃO
# ============================================================

LOGIN_URL = "/login/"

LOGIN_REDIRECT_URL = "/"

LOGOUT_REDIRECT_URL = "/login/"


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# ============================================================
# SEGURANÇA EM PRODUÇÃO
# ============================================================

if not DEBUG:

    # Render funciona atrás de um proxy HTTPS.
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_REFERRER_POLICY = "same-origin"

    X_FRAME_OPTIONS = "DENY"


# ============================================================
# CHAVE PRIMÁRIA PADRÃO
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"