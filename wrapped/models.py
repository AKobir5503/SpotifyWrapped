from django.db import models
from django.contrib.auth.models import User

# Model for SpotifyWrap
class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spotify_wraps')
    top_tracks = models.JSONField()  # Native JSONField for top tracks
    top_artists = models.JSONField()  # Native JSONField for top artists
    top_genres = models.JSONField()  # Native JSONField for top genres
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wrap for {self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"

# Model for more generic Wrap
class Wrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wraps')
    name = models.CharField(max_length=255)  # Name of the wrap
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Native JSONField for wrap data

    def __str__(self):
        return f"{self.name} by {self.user.username}"
