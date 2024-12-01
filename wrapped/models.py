from django.db import models
from django.contrib.auth.models import User

# Model for SpotifyWrap

class SpotifyWrap(models.Model):
    """
    Represents a Spotify Wrapped data set for a user.

    Attributes:
        user (User): The user who owns this Spotify Wrapped.
        name (str): Title or name of the wrap. (e.g., "Top Tracks - Short Term")
        time_frame (str): The time frame of the data. (e.g., 'short_term', 'medium_term', 'long_term')
        created_at (datatime): The timestap when the wrap was created.
        data (JSONField): A JSON object containing Spotify-related data such as top tracks, artists, genres, etc.

    Methods:
        __str__(): Returns a string representation of the wrap, including the username and time frame.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="spotify_wraps")
    name = models.CharField(max_length=255)  # Title or name of the wrap
    time_frame = models.CharField(max_length=50)  # e.g., 'short_term', 'medium_term', 'long_term'
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Store the actual Spotify data, like top tracks, artists, etc.

    def __str__(self):
        """
        Provides a string representation of the SpotifyWrap instance.

        Returns:
            str: A string in the format "<username>'s wrap for <time_frame>".
        """
        return f"{self.user.username}'s wrap for {self.time_frame}"


# Model for more generic Wrap
class Wrap(models.Model):
    """
    Represents a generic wrap for a user, not limited to Spotify data.

    Attributes:
        user (User): The user who owns this wrap.
        name (str): The name of the wrap (e.g., "2024 Music Highlights").
        created_at (datetime): The timestamp when the wrap was created.
        data (JSONField): A JSON object containing generic wrap data.

    Methods:
        __str__(): Returns a string representation of the wrap, including its name and the username of the owner.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wraps')
    name = models.CharField(max_length=255)  # Name of the wrap
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()  # Native JSONField for wrap data

    def __str__(self):
        """
        Provides a string representation of the Wrap instance.

        Returns:
            str: A string in the format "<wrap_name> by <username>".
        """

        return f"{self.name} by {self.user.username}"
