try:
    from project.global_settings import *  # nopycln: import
except ImportError:
    pass

from glob import glob
from os import environ
from os.path import abspath, dirname, join

import sentry_sdk
import yaml
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = dirname(dirname(abspath(__file__)))


def load_environment_variables_from_docker_compose_file():
    try:
        with open(join(dirname(BASE_DIR), "docker-compose/.dev.yaml"), "r") as stream:
            content = yaml.safe_load(stream)
            for key, value in content["services"]["backend"]["environment"].items():
                if key not in environ:
                    environ[key] = str(value)

    except FileNotFoundError:
        pass  # Expected when using docker-compose


load_environment_variables_from_docker_compose_file()

SECRET_KEY = environ["SECRET_KEY"]

DEBUG = bool(int(environ["DEBUG"]))
TEST = bool(int(environ["TEST"]))
ENVIRONMENT = environ.get("ENVIRONMENT", "local")

FULL_HOSTNAME = environ["FULL_HOSTNAME"]
ALLOWED_HOSTS = environ["ALLOWED_HOSTS"].split(",")

# linux
# sudo apt-get install binutils libproj-dev gdal-bin
# mac
# brew install postgresql
# brew install postgis
# brew install gdal
# brew install libgeoip
try:
    GDAL_LIBRARY_PATH = (
        glob("/usr/lib/libgdal.so.*") + glob("/usr/lib/*/libgdal.so.*")
    )[0]
    GEOS_LIBRARY_PATH = (
        glob("/usr/lib/libgeos_c.so.*") + glob("/usr/lib/*/libgeos_c.so.*")
    )[0]
except IndexError:
    pass

# Application definition

INSTALLED_APPS = [
    # 'dal',
    # 'dal_select2',
    "admin_numeric_filter",
    "project.apps.MyAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rangefilter",
    "nested_admin",
    "rest_framework",
    "rest_framework_gis",
    "rest_framework.authtoken",
    "phonenumber_field",
    "corsheaders",
    "bis",
    "categories",
    "questionnaire",
    "feedback",
    "event",
    "other",
    "donations",
    "administration_units",
    # "debug_toolbar",
    "login_code",
    "ecomail",
    "solo",
    "admin_auto_filters",
    "django_filters",
    "tinymce",
    "opportunities",
    "more_admin_filters",
    "regions",
    "drf_spectacular",
    "oauth2_provider",
    "oauth_dcr",
    "mcp_server",
    "game_book",
    "game_book_categories",
    "cookbook",
    "cookbook_categories",
    "django_bootstrap5",
    "django_cleanup.apps.CleanupConfig",  # needs to be last
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE.insert(0, "bis.middleware.sql_middleware")
    # MIDDLEWARE.insert(
    #     0,
    #     "debug_toolbar.middleware.DebugToolbarMiddleware",
    # )

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": environ["DB_HOST"],
        "PORT": environ["DB_PORT"],
        "NAME": environ["DB_NAME"],
        "USER": environ["DB_USERNAME"],
        "PASSWORD": environ["DB_PASSWORD"],
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

#
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = ["bis.auth_backend.BISBackend"]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "cs"
TIME_ZONE = "Europe/Prague"
USE_I18N = True
USE_TZ = True
DATE_FORMAT = "j. n. Y"
SHORT_DATE_FORMAT = DATE_FORMAT
DATE_INPUT_FORMATS = [
    "%d. %m. %Y",
    "%d.%m.%Y",
    "%Y-%m-%d",
]
TIME_FORMAT = "G:i"
TIME_INPUT_FORMATS = [
    "%H:%M:%S",
    "%H:%M:%S.%f",
    "%H:%M",
]
DATETIME_FORMAT = f"{DATE_FORMAT}, {TIME_FORMAT}"
SHORT_DATETIME_FORMAT = DATETIME_FORMAT
DATETIME_INPUT_FORMATS = [
    date_format + separator + time_format
    for date_format in DATE_INPUT_FORMATS
    for separator in [" ", ", "]
    for time_format in TIME_INPUT_FORMATS
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/backend_static/"
MEDIA_URL = "/media/"

STATIC_ROOT = join(BASE_DIR, "backend_static")
MEDIA_ROOT = join(BASE_DIR, "media")

#
# Upload limits
# https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-DATA_UPLOAD_MAX_MEMORY_SIZE
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

#
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.helpers.Pagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
TOKEN_EXPIRE_AFTER_INACTIVITY_SECONDS = 20 * 60

# OAuth2 Provider settings (django-oauth-toolkit)
OAUTH2_PROVIDER = {
    "SCOPES": {
        "mcp": "MCP server access",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": None,
    "REFRESH_TOKEN_EXPIRE_SECONDS": None,
    "ROTATE_REFRESH_TOKEN": False,
    "ALLOWED_REDIRECT_URI_SCHEMES": ["https", "http"] if DEBUG else ["https"],
    # PKCE is required for public clients
    "PKCE_REQUIRED": True,
}

# Dynamic Client Registration settings (for Claude AI integration)
OAUTH2_DCR = {
    "OPEN_REGISTRATION": True,  # Allow clients to register without authentication
    "DEFAULT_SCOPES": ["mcp"],
    "ALLOWED_GRANT_TYPES": [
        "authorization_code",
    ],
}

# MCP Server settings
DJANGO_MCP_GLOBAL_SERVER_CONFIG = {
    "name": "bis-mcp",
    "instructions": "BIS (Brontosaurus Information System) MCP server. "
    "Provides access to event management, user profiles, and organization data.",
    "stateless": False,
}

DJANGO_MCP_AUTHENTICATION_CLASSES = [
    "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
]

SPECTACULAR_SETTINGS = {
    "TITLE": "BIS API",
    "DESCRIPTION": "API Brontosauřího informačního systému, veřejné pro web, interní pro frontend",
    "VERSION": "1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# API settings
API_BASE = environ["API_BASE"]

if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [FULL_HOSTNAME]
    CORS_ALLOWED_ORIGINS = [FULL_HOSTNAME]

    if "dev" in FULL_HOSTNAME:
        CSRF_TRUSTED_ORIGINS += ["http://localhost", "http://localhost:3000"]
        CORS_ALLOWED_ORIGINS += ["http://localhost", "http://localhost:3000"]

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# phonenumber_field
PHONENUMBER_DEFAULT_REGION = "CZ"
PHONENUMBER_DEFAULT_FORMAT = "INTERNATIONAL"

# sentry.io logging
if not DEBUG:
    sentry_sdk.init(
        dsn=environ["SENTRY_DSN"],
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=0.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        environment=ENVIRONMENT,
    )

# app
APP_NAME = environ["APP_NAME"]

EMAIL = environ["EMAIL"]

AUTH_USER_MODEL = "bis.User"

SKIP_VALIDATION = False
EMAILS_ENABLED = bool(int(environ["EMAILS_ENABLED"]))

ECOMAIL_API_KEY = environ["ECOMAIL_API_KEY"]

# darujme
DARUJME_API_KEY = environ.get("DARUJME_API_KEY")
DARUJME_SECRET = environ.get("DARUJME_SECRET")

HCAPTCHA_SECRET = environ["HCAPTCHA_SECRET"]
GROQ_API_KEY = environ["GROQ_API_KEY"]

if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
    DEBUG_TOOLBAR_CONFIG = {"PROFILER_MAX_DEPTH": 20}

TINYMCE_DEFAULT_CONFIG = {
    "menubar": False,
    "plugins": "autolink,lists,link,image,charmap,preview,searchreplace,"
    "fullscreen,paste,code,help,wordcount,media",
    "toolbar": "undo redo | formatselect | bold italic | "
    "bullist numlist | link emoticons | fullscreen removeformat | help",
    "toolbar_mode": "wrap",
    "block_formats": "Paragraph=p; Nadpis=h3",
    "fontsize_formats": "12pt",
}

THUMBNAIL_SIZES = {
    "small": 352,
    "medium": 720,
    "large": 1920,
}

BOOTSTRAP5 = {
    "required_css_class": "required",
    "field_renderers": {
        "default": "game_book.filters.GameBookFieldRenderer",
    },
}
LOGIN_URL = "/logout"

# Logging configuration
LOG_DIR = join(BASE_DIR, "logs")
LOG_FILE = join(LOG_DIR, "bis.log")

# Create logs directory if it doesn't exist
from pathlib import Path

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 50,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}
