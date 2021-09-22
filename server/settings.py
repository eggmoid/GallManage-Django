"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import ignore_logger

import json
import os
from os.path import join
import redis

from pathlib import Path

from django.core.exceptions import SuspiciousOperation
from django.core.validators import validate_ipv46_address
from rest_framework.exceptions import ValidationError

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
secret_file = os.path.join(BASE_DIR, 'server/secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        raise KeyError(f'Set the {setting} environment variable')


sentry_sdk.init(
    dsn=get_secret('SENTRY_DSN'),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True)
ignore_logger("django.security.DisallowedHost")

SECRET_KEY = get_secret('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_secret('DEBUG')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost'] + get_secret('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'api.models',
    'api.models.detail_post',
    'api.models.post',
    'api.models.post_back',
    'api.models.post_rank',
    'server',
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('config.permissions.IsAdminUser',),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE':
        20,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'fileFormat': {
            'format':
                '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
            'datefmt':
                '%d/%b/%Y %H:%M:%S'
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': join(BASE_DIR, 'logfile.log'),
            'formatter': 'fileFormat'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': join(BASE_DIR, 'server.log'),
            'formatter': 'django.server',
        }
    },
    'loggers': {
        'django.db.backends': {
            # 'handlers': ['console'],
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}


class XForwardedForMiddleware:
    """
    Set REMOTE_ADDR if it's missing because of a reverse proxy (nginx + gunicorn) deployment.
    https://stackoverflow.com/questions/34251298/empty-remote-addr-value-in-django-application-when-using-nginx-as-reverse-proxy
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            remote_addrs = request.META['HTTP_X_FORWARDED_FOR'].split(',')
            remote_addr = None

            # for some bots, 'unknown' was prepended as the first value: `unknown, ***.***.***.***`
            # in which case the second value actually is the correct one
            for ip in remote_addrs:
                ip = self._validated_ip(ip)
                if ip is not None:
                    remote_addr = ip
                    break

            if remote_addr is None:
                raise SuspiciousOperation('Malformed X-Forwarded-For.')

            request.META['HTTP_X_PROXY_REMOTE_ADDR'] = request.META[
                'REMOTE_ADDR']
            request.META['REMOTE_ADDR'] = remote_addr

        return self.get_response(request)

    def _validated_ip(self, ip):
        ip = ip.strip()
        try:
            validate_ipv46_address(ip)
        except ValidationError:
            return None
        return ip


MIDDLEWARE = [
    'server.settings.XForwardedForMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'drf_yasg.middleware.SwaggerExceptionMiddleware',
]

ROOT_URLCONF = 'server.urls'

SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login',
    'LOGOUT_URL': '/admin/logout',
    'DEFAULT_INFO': 'server.urls.swagger_info',
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'server.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': get_secret('DB_SERVICE'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'CONN_MAX_AGE': None,
        'OPTIONS': {
            'threaded': True,
        }
    }
}

# Celery
CELERY_BROKER_URL = get_secret('BROKER_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_BACKEND = get_secret('CELERY_RESULT_BACKEND')
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_ENABLE_UTC = False

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MONITOR_URL = get_secret('MONITOR_URL')
MONITOR = redis.Redis.from_url(MONITOR_URL)
