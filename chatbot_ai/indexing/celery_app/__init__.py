from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging

logger = logging.getLogger(__name__)

app = Celery("indexing")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys

#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Use Django Beat scheduler
app.conf.beat_scheduler = 'django_celery_beat.schedulers.DatabaseScheduler'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
