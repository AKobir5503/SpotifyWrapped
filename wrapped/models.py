from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wrap_data = models.JSONField()  # Store the wrap data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
