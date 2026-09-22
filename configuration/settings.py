from pathlib import Path
import os
import sys
import dj_database_url


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SEGURANÇA
# ============================================================

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-local-development-only-change-in-production",
)

DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")


# Hosts permitidos
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

extra_allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")

if extra_allowed_hosts:
    ALLOWED_HOSTS.extend(
        host.strip()
        for host in extra_allowed_hosts.split(",")
        if host.strip()
    )


# ============================================================
# APLICAÇÕES DO PROJETO
# ============================================================

APPS_DIR = BASE_DIR / "apps"

if str(APPS_DIR) not in sys.path:
    sys.path.append(str(APPS_DIR))


INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Bibliotecas
    "colorfield",
    "ckeditor",
    "ckeditor_uploader",
    "django_select2",

    # Aplicações do sistema
    "core",
    "users",
    "rest_framework",
    "agenda",
    "despesa",
]


# ============================================================
# CKEDITOR
# ============================================================

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    "default": {
        "skin": "moono-lisa",
        "toolbar": "Custom",
        "toolbar_Custom": [
            [
                "NumberedList",
                "BulletedList",
                "Print",
                "Outdent",
                "Indent",
                "-",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
                "RemoveFormat",
                "SelectAll",
                "Maximize",
                "Strike",
                "Select",
                "Save",
            ],
            [
                "Cut",
                "Copy",
                "Paste",
                "Undo",
                "Redo",
                "Bold",
                "Italic",
                "Underline",
                "Image",
                "Link",
                "Unlink",
                "TextColor",
                "BGColor",
                "Find",
                "Preview",
                "NewPage",
                "PageBreak",
                "a11yhelp",
                "Table",
                "About",
            ],
            [
                "Styles",
                "Format",
                "Font",
                "FontSize",
            ],
        ],
        "width": "100%",
    },
    "DescricaoServico": {
        "skin": "moono-lisa",
        "toolbar": "Custom",
        "toolbar_Custom": [
            [
                "NumberedList",
                "BulletedList",
                "Print",
                "Outdent",
                "Indent",
                "JustifyLeft",
                "JustifyCenter",
                "JustifyRight",
                "JustifyBlock",
                "RemoveFormat",
                "SelectAll",
                "Maximize",
                "Strike",
                "Select",
                "Save",
            ],
            [
                "Cut",
                "Copy",
                "Paste",
                "Undo",
                "Redo",
                "Bold",
                "Italic",
                "Underline",
                "Link",
                "Unlink",
                "TextColor",
                "BGColor",
                "Find",
                "Preview",
                "NewPage",
                "PageBreak",
                "a11yhelp",
                "Table",
                "About",
            ],
            [
                "Styles",
                "Format",
                "Font",
                "FontSize",
            ],
        ],
        "width": "100%",
    },
}


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Arquivos estáticos em produção
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

ROOT_URLCONF = "configuration.urls"


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
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "users.views.base",
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "configuration.wsgi.application"


# ============================================================
# USUÁRIO
# ============================================================

AUTH_USER_MODEL = "users.User"

LOGIN_REDIRECT_URL = "home"

LOGOUT_REDIRECT_URL = "/"


# ============================================================
# BANCO DE DADOS
# ============================================================

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
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
# VALIDAÇÃO DE SENHA
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

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# WhiteNoise
STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# ============================================================
# ARQUIVOS DE MÍDIA
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# CSRF / ORIGENS DE CONFIANÇA
# ============================================================

csrf_trusted_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")

if csrf_trusted_origins:
    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in csrf_trusted_origins.split(",")
        if origin.strip()
    ]
else:
    CSRF_TRUSTED_ORIGINS = []


# ============================================================
# CONFIGURAÇÕES DE PRODUÇÃO
# ============================================================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"