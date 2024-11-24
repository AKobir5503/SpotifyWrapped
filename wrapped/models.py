from django.db import models
from django.contrib.auth.models import User

# Model for SpotifyWrap

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spotify_wraps")
    name = models.CharField(max_length=255)  # Title or name of the wrap
    time_frame = models.CharField(max_length=50)  # e.g., 'short_term', 'medium_term', 'long_term'
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store the actual Spotify data, like top tracks, artists, etc.

    def __str__(self):
        return f"{self.user.username}'s wrap for {self.time_frame}"

# Model for more generic Wrap
class Wrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wraps')
    name = models.CharField(max_length=255)  # Name of the wrap
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Native JSONField for wrap data

    def __str__(self):
        return f"{self.name} by {self.user.username}"
