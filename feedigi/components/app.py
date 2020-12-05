# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ua4kk5)f&tp0@b23i+@p0xq021s4-rwqo=c6^z90!o7_kk29z!'

# Application definition

INSTALLED_APPS = [
    'jet.dashboard',
    'jet',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'markdownx',

    'corsheaders',
    'rest_framework',

    'common',
    'user',
    'feed'

]

ROOT_URLCONF = 'feedigi.urls'
