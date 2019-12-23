"""
With these settings, tests run faster.
"""

# import os

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False  # Currently leaving False as it doesn't seem to alter login
               # behaviour
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY",
                 default="CgFRMUqNikKjbHT9KXLsgJj3tzTSEQlTnE31UzXZYp90LMgk96dbCWsAmORceGfK")
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": ""
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# Your stuff...
# ------------------------------------------------------------------------------
# if env('USE_DOCKER') == 'yes':
#     import socket
#     hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
#     INTERNAL_IPS += [ip[:-1] + '1' for ip in ips]
# os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = "localhost:8000-8010,8080,9200-9300"
# os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = "localhost:8001"
# DJANGO_LIVE_TEST_SERVER_ADDRESS = "0.0.0.0:8001"

# DATABASES['default'] = env.db('DATABASE_URL')  # noqa F405
# DATABASES['default']['TEST'] = env.db('DATABASE_URL')  # noqa F405
# DATABASES['default']['CONN_MAX_AGE'] = env.int('CONN_MAX_AGE', default=60)  # noqa F405
