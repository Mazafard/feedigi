import os

from feedigi.components.app import BASE_DIR

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SERVER_STAGE = os.getenv('_SERVER_STAGE', 'Release Candidate')

EMAIL_VERIFICATION_CODE_SIZE = 32

# Slack channel to report logs
SLACK_REPORT_CHANNEL = None


# Server Auth
SERVER_AUTHENTICATION = os.getenv('_SERVER_AUTHENTICATION', '1234567890')


