from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    top_tracks = models.JSONField()  # Stores top tracks data as a JSON
    top_artists = models.JSONField()  # Stores top artists data as a JSON
    top_genres = models.JSONField()  # Stores top genres data as a JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wrap for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

