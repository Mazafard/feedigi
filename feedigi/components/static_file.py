import os

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static/'
UPLOAD_DIRECTORY = os.getenv('_UPLOAD_DIRECTORY', 'uploads')
CDN_DOMAIN = os.getenv('_CDN_DOMAIN', 'http://127.0.0.1:3400/')
APPLICATION_BASE_URL = os.getenv('_APPLICATION_BASE_URL', 'http://localhost:8000')

UPLOAD_FOLDER = os.getenv("_UPLOAD_FOLDER", "uploads")
MEDIA_ROOT = UPLOAD_FOLDER + "/media"
MEDIA_URL = '/uploads/media/'
ATTACHMENTS_ROOT = MEDIA_ROOT + "/attachments"
ATTACHMENTS_URL = MEDIA_URL + "attachments/"
