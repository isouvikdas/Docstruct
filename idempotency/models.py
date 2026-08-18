from django.db import models

# Create your models here.

class IdempotencyRecord(models.Model):
    STATUS_CHOICES = [
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed')
    ]

    key = models.CharField(max_length=255, unique=True),
    endpoint = models.CharField(max_length=255),
    request_hash = models.CharField(max_length=64),
    status_code = models.PositiveIntegerField(null=True),
    created_at = models.DateTimeField(auto_now_add=True),
    expires_at = models.DateTimeField(),
    response_body = models.JSONField(null=True),
    state = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROCESSING')

    def __str__(self):
        return self.key, self.endpoint, self.request_hash, self.status_code, self.response_body