import os
from datetime import timedelta

# 5 minutes cache
CACHE_MIDDLEWARE_SECONDS = 300

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        'rest_framework.permissions.DjangoModelPermissions',
        "rest_framework.permissions.AllowAny"
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.base.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # for swagger schema class
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'iFLEET API Documentation',
    'DESCRIPTION': 'Detailed API documentation for iFLEET project with drf-spectacular',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'ENUM_NAME_OVERRIDES': {
        'apps.operation.models.Inspection.type': 'apps.client.enums.InspectionType',
        'apps.operation.models.DriverEvent.type': 'apps.client.enums.DriverEventType',
        'apps.operation.models.VehicleInspection.status': 'apps.client.enums.InspectionStatus',
        'apps.operation.models.Reservation.status': 'apps.operation.enums.ReservationStatus',
        'apps.operation.models.DrivingReport.status': 'apps.operation.enums.DriverStatus',
        'apps.user.models.User.status': 'apps.user.enums.UserStatus',
        'apps.user.models.User.type': 'apps.user.enums.UserType',
    },
}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('Bearer',),
   'ACCESS_TOKEN_LIFETIME': timedelta(minutes=600000),
}


# Django app vars | CORS
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_ALLOW_HEADER = [
    'username',
    'group',
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_HEADERS = '*'
CORS_ALLOW_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',]

# celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_RESULT_EXPIRES = 3600
CELERY_TASK_DEFAULT_QUEUE = 'backend.celery'
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
