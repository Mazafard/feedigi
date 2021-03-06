"""
Django settings for feedigi project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

from split_settings.tools import optional, include

include(
    'components/app.py',
    'components/middleware.py',
    'components/wsgi.py',
    'components/template.py',
    'components/auth.py',
    'components/rest_framework.py',
    'components/i18n.py',
    'components/logger.py',
    'components/static_file.py',
    'components/cors.py',
    'components/environments.py',
    scope=globals()
)
