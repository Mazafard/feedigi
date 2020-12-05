# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/
import os

from feedigi.components.app import BASE_DIR

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = False

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = (
    ('fa', 'Farsi'),
    ('en', 'English'),
)

