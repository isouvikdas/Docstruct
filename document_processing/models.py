from django.db import models
import uuid

# Create your models here.

class Document(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_key = models.CharField(max_length=500, default="")
    original_filename = models.CharField(max_length=250, default="")
    file_size = models.IntegerField(null=True, blank=True)
    file_url = models.URLField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(null = True, blank=True)
    error_text = models.TextField(null = True, blank=True)
    
    def __str__(self):
        return str(self.id)
    
        
