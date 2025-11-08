# DASH/celery.py
import os
from DASH.celery_app import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DASH.settings')
app = Celery('DASH')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()