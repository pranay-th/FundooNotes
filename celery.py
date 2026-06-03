import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fundoonotes.settings")

app = Celery("fundoonotes")

# Load task-related configuration from Django settings using the CELERY namespace.
# This means all Celery config keys in settings.py must be prefixed with CELERY_
# (e.g. CELERY_BROKER_URL, CELERY_RESULT_BACKEND, etc.)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed Django apps (looks for tasks.py in each app).
app.autodiscover_tasks()
