from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    This allows us to add additional fields to the user model if needed.
    """
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    def __str__(self):
        return self.username 