from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = {
        ('ADMIN', 'Admin'),
        ('USER', 'User')
    }
    
    role = models.CharField(max_length=120, choices=ROLE_CHOICES)