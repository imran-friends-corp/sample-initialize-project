# core
import os
import logging

# celery
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# Set up logging to a file
# logger = logging.getLogger(__name__)

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.timezone = 'UTC'

app.conf.beat_schedule = {
    "update_driverprofile_age": {
        "task": "apps.operation.tasks.update_driverprofile_age",
        "schedule": crontab(minute=0, hour=17, day_of_month=1),
    }
}
