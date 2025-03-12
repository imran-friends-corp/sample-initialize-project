import os
from dotenv import load_dotenv

load_dotenv()

# Django app vars
AUTH_USER_MODEL = 'user.User'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = False

# Django app vars | From .env
# ALLOWED_HOSTS = '*'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*,').split(',')
# DEBUG = True
DEBUG = os.environ.get('DEBUG', False) == 'True'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

CSRF_TRUSTED_ORIGINS = os.environ.get('TRUSTED_ORIGINS', '*,').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*,').split(',')

# Email vars
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND')
DEFAULT_EMAIL = os.environ.get('DEFAULT_EMAIL')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', False) == 'True'
EMAIL_INVITATION_EXPIRY_HOUR = os.environ.get('EMAIL_INVITATION_EXPIRY_HOUR', 72)


# OTP
OTP_SECRET = os.environ.get('OTP_SECRET', '*oN27E-pdj')
OTP_SECRET_KEY = os.environ.get('OTP_SECRET_KEY', "otp_g845dfs8df121hgjh")
OTP_VERIFY_SECRET_KEY = os.environ.get('OTP_VERIFY_SECRET_KEY', "otp_verify_54g54g4fg2")
OTP_EXPIRY_MIN = os.environ.get('OTP_EXPIRY_MIN', 5)
DEFAULT_OTP = int(os.environ.get('DEFAULT_OTP', 777777))

# Database
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = int(os.environ.get('DB_PORT'))

# Mongo Database
MONGO_URI = os.environ.get('MONGO_URI')
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')

# Third parties | Broker
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
CELERY_ENABLED = bool(os.environ.get('CELERY_ENABLED', False))

# Third parties | AWS
AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME')
AWS_SES_ACCESS_KEY_ID = os.environ.get('EMAIL_HOST_USER')
AWS_SES_SECRET_ACCESS_KEY = os.environ.get('EMAIL_HOST_PASSWORD')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
DEFAULT_FILE_STORAGE = 'backend.settings.s3_storage.S3MediaStorage'
AWS_QUERYSTRING_AUTH = False

APPEND_SLASH = False
