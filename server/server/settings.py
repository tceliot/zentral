"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import os
from django.core.management import utils
# Import the zentral settings (base.json)
from zentral.conf import settings as zentral_settings
from .celery import app as celery_app

__all__ = ('celery_app',)

django_zentral_settings = zentral_settings.get('django', {})

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = django_zentral_settings.get('SECRET_KEY', utils.get_random_secret_key())
SECRET_KEY_FALLBACKS = django_zentral_settings.get('SECRET_KEY_FALLBACKS', [])

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = django_zentral_settings.get('DEBUG', False)

ALLOWED_HOSTS = list(django_zentral_settings.get('ALLOWED_HOSTS', []))
if not ALLOWED_HOSTS:
    fqdn = zentral_settings.get("api", {}).get("fqdn")
    if fqdn:
        ALLOWED_HOSTS.append(fqdn)
    fqdn_mtls = zentral_settings.get("api", {}).get("fqdn_mtls")
    if fqdn_mtls:
        ALLOWED_HOSTS.append(fqdn_mtls)

if "CACHES" in django_zentral_settings:
    CACHES = django_zentral_settings["CACHES"]

# django default is 2.5MB. increased to 10MB.
DATA_UPLOAD_MAX_MEMORY_SIZE = django_zentral_settings.get('DATA_UPLOAD_MAX_MEMORY_SIZE', 10485760)

# Email configuration

DEFAULT_FROM_EMAIL = django_zentral_settings.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

EMAIL_BACKEND = django_zentral_settings.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = django_zentral_settings.get("EMAIL_HOST", 'localhost')
EMAIL_PORT = django_zentral_settings.get("EMAIL_PORT", 25)
EMAIL_HOST_USER = django_zentral_settings.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = django_zentral_settings.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = django_zentral_settings.get("EMAIL_USE_TLS", False)
EMAIL_USE_SSL = django_zentral_settings.get("EMAIL_USE_SSL", False)
EMAIL_TIMEOUT = django_zentral_settings.get("EMAIL_TIMEOUT")
EMAIL_SSL_KEYFILE = django_zentral_settings.get("EMAIL_SSL_KEYFILE")
EMAIL_SSL_CERTFILE = django_zentral_settings.get("EMAIL_SSL_CERTFILE")
EMAIL_FILE_PATH = django_zentral_settings.get("EMAIL_FILE_PATH")

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrapform',
    'rest_framework',
    'django_filters',
    'django_celery_results',
    'accounts',
    'base',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'accounts.api_authentication.APITokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    # disable the Browsable API Renderer
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = django_zentral_settings.get("AUTH_PASSWORD_VALIDATORS", [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "accounts.password_validation.PasswordNotAlreadyUsedValidator",
    },
])

AUTHENTICATION_BACKENDS = [
    'accounts.auth_backends.ZentralBackend',
    'realms.auth_backends.RealmBackend',
]

# SESSION*
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = django_zentral_settings.get("SESSION_COOKIE_SAMESITE", "Lax")

if "SESSION_COOKIE_AGE" in django_zentral_settings:
    SESSION_COOKIE_AGE = django_zentral_settings["SESSION_COOKIE_AGE"]

if "SESSION_EXPIRE_AT_BROWSER_CLOSE" in django_zentral_settings:
    SESSION_EXPIRE_AT_BROWSER_CLOSE = django_zentral_settings["SESSION_EXPIRE_AT_BROWSER_CLOSE"]

# CSRF*
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Strict"
if "CSRF_TRUSTED_ORIGINS" in django_zentral_settings:
    CSRF_TRUSTED_ORIGINS = django_zentral_settings["CSRF_TRUSTED_ORIGINS"]

MAX_PASSWORD_AGE_DAYS = django_zentral_settings.get("MAX_PASSWORD_AGE_DAYS", None)

LOGIN_REDIRECT_URL = '/'

# add the zentral apps
for app_name in zentral_settings.get('apps', []):
    INSTALLED_APPS.append(app_name)

MIDDLEWARE = [
    'base.middlewares.never_cache_middleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'realms.middlewares.realm_session_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'base.middlewares.csp_middleware',
    'base.middlewares.deployment_info_middleware',
]

STATIC_WHITENOISE = django_zentral_settings.get("STATIC_WHITENOISE", False)
if STATIC_WHITENOISE:
    MIDDLEWARE.insert(MIDDLEWARE.index("django.middleware.security.SecurityMiddleware") + 1,
                      "whitenoise.middleware.WhiteNoiseMiddleware")

if MAX_PASSWORD_AGE_DAYS:
    MIDDLEWARE.insert(MIDDLEWARE.index("django.contrib.messages.middleware.MessageMiddleware") + 1,
                      "accounts.middleware.force_password_change_middleware")

ROOT_URLCONF = 'server.urls'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'templates/forms')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'zentral.conf.context_processors.extra_links',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 3600
    }
}
for key, default in (('HOST', None),
                     ('PORT', None),
                     ('NAME', 'zentral'),
                     ('USER', 'zentral'),
                     ('PASSWORD', None),):
    config_key = 'POSTGRES_{}'.format(key)
    val = django_zentral_settings.get(config_key, default)
    if val:
        DATABASES['default'][key] = val

# Django >= 3.2 have uses BigAutoField
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = django_zentral_settings.get("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
CELERY_BROKER_TRANSPORT_OPTIONS = django_zentral_settings.get("CELERY_BROKER_TRANSPORT_OPTIONS", {})

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = django_zentral_settings.get("LANGUAGE_CODE", "en-us")

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
if DEBUG:
    STATIC_URL = '/static_debug/'
else:
    if STATIC_WHITENOISE:
        STATIC_URL = '/static_whitenoise/'
    else:
        STATIC_URL = '/static/'
STATIC_ROOT = django_zentral_settings.get("STATIC_ROOT", "/zentral_static")

# Directory that will hold the files if the default file storage is used
MEDIA_ROOT = django_zentral_settings.get("MEDIA_ROOT", "")

# Storages
STORAGES = django_zentral_settings.get("STORAGES", {})
if "default" not in STORAGES:
    STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
if "staticfiles" not in STORAGES:
    STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"}


# LOGGING
# everything in the console.


log_formatter = django_zentral_settings.get("LOG_FORMATTER")
if log_formatter:
    log_formatter_dict = {'()': log_formatter}
    # this log formatter option can be used for example to configure the JSON output
    # the warnings are not formatted, and can cause some parsing issues
    # → disable all warnings when not in DEBUG mode
    if not DEBUG:
        import sys
        if not sys.warnoptions:
            import warnings
            warnings.simplefilter("ignore")
else:
    log_asctime = django_zentral_settings.get("LOG_ASCTIME", True)
    log_formatter_dict = {
        'format': '{}PID%(process)d %(module)s %(levelname)s %(message)s'.format('%(asctime)s ' if log_asctime else '')
    }


if DEBUG:
    log_level = "DEBUG"
else:
    log_level = "INFO"


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'ztl_formatter': log_formatter_dict
    },
    'handlers': {
        'console': {
            'level': log_level,
            'class': 'logging.StreamHandler',
            'formatter': 'ztl_formatter',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
        },
        'py.warnings': {
            'handlers': ['console'],
        },
        'server': {
            'handlers': ['console'],
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['console'],
        },
        'zentral': {
            'level': log_level,
            'handlers': ['console'],
        },
        # dependencies
        'elasticsearch': {
            'level': 'ERROR',
            'handlers': ['console'],
        },
        'hpack': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
    }
}
