from django.db import models
from django.contrib.auth.models import User

# Model for SpotifyWrap

class SpotifyWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spotify_wraps")
    name = models.CharField(max_length=255)  # Title or name of the wrap
    time_frame = models.CharField(max_length=50)  # e.g., 'short_term', 'medium_term', 'long_term'
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store the actual Spotify data, like top tracks, artists, etc.
    share_token = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Generate a unique token before saving
        if not self.share_token:
            self.share_token = str(uuid.uuid4())[:12]  # Use the first 12 characters of UUID
        super().save(*args, **kwargs)

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
