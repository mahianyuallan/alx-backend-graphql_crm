import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')

app = Celery('crm')

# Load configuration from Django settings, using a namespace.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
