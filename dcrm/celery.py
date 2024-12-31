import os
from celery.schedules import crontab
from celery import Celery
from django.conf import settings
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dcrm.settings')

app = Celery('dcrm')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'create-monthly-table': {
        'task': 'website.tasks.create_monthly_table',
        'schedule': crontab(day_of_week=0, hour=0, minute=0),
    },
    'backup-and-clear-data': {
        'task': 'website.tasks.backup_and_clear_data',
        'schedule': crontab(day_of_week=0, hour=0, minute=30),  # Make sure this runs after the table creation
    },
}


# celery -A dcrm worker --pool=solo -l info
# celery -A dcrm beat -l info
    
# watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A dcrm worker  --concurrency=1 -l info
    


# Worker = watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A dcrm worker --pool=solo --concurrency=1 -l info
# Beat = watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A dcrm beat -l info