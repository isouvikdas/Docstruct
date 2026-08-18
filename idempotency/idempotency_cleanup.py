from celery import Celery
from idempotency.models import IdempotencyRecord
from django.utils import timezone
from document_processing.celery import app

@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    """Call delete expired keys every hour"""
    sender.add_periodic_task(3600, delete_expired_keys(), name='Cleanup expired keys')

@app.task
def delete_expired_keys():
    IdempotencyRecord.objects.filter(expires_at__lt=timezone.now()).delete()