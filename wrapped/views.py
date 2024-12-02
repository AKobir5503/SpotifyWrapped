import random

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import requests
from django.contrib.auth import logout
from .models import SpotifyWrap, Wrap
from django.urls import reverse
from collections import Counter
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from collections import defaultdict
import os

# use the settings instead of hardcoded values
SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET


if 'DYNO' in os.environ:  # Heroku environment
    SPOTIFY_REDIRECT_URI = 'https://spotifywrapped35-7ed41b719d25.herokuapp.com/callback/'
else:  # Local environment
    SPOTIFY_REDIRECT_URI = 'http://localhost:8000/callback/'
#SPOTIFY_REDIRECT_URI = 'http://localhost:8000/callback/'

# Landing page view
def landing(request):
    """
        Handles the landing page with support for view mode and language preferences.

        - Saves user preferences for `view_mode` and `language` in the session.
        - Renders the appropriate localized landing page template.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered landing page template.
        """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        if language == "en":
            return render(request, "landing.html", {"view_mode": view_mode})
        elif language == "de":
            return render(request, "landing_de.html", {"view_mode": view_mode})
        elif language == "es":
            return render(request, "landing_es.html", {"view_mode": view_mode})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    if language == "en":
        return render(request, "landing.html", {"view_mode": view_mode})
    elif language == "de":
        return render(request, "landing_de.html", {"view_mode": view_mode})
    elif language == "es":
        return render(request, "landing_es.html", {"view_mode": view_mode})

# Login view
def login_user(request):
    """
        Handles user login, authentication, and session preference settings.

        - Authenticates user with provided username and password.
        - Saves view mode and language preferences in the session.
        - Redirects authenticated users to the dashboard.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The login page or a redirect to the dashboard.
    """
    if request.method == "POST":
        # Handle view mode and language settings
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        # Handle authentication
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")  # Redirect to user dashboard
        else:
            return render(
                request,
                "login.html",
                {
                    "error": "Invalid credentials",
                    "view_mode": view_mode,
                    "language": language,
                }
            )

    # Retrieve view mode and language settings from the session
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    if language == "en":
        return render(request, "login.html", {"view_mode": view_mode})
    elif language == "de":
        return render(request, "login_de.html", {"view_mode": view_mode})
    elif language == "es":
        return render(request, "login_es.html", {"view_mode": view_mode})

# Register user view
def register_user(request):
    """
        Handles user registration with session preference settings.

        - Processes the registration form.
        - Saves view mode and language preferences in the session.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The registration page or a redirect to the login page.
    """
    # Handle "view_mode" and "language" for GET and POST requests
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            # Save the settings to the session
            request.session["view_mode"] = request.POST.get("view_mode", view_mode)
            request.session["language"] = request.POST.get("language", language)

            return redirect('login')
    else:
        form = UserCreationForm()

    if language == "en":
        return render(request, "register.html", {"view_mode": view_mode,'form': form,})
    elif language == "de":
        return render(request, "register_de.html", {"view_mode": view_mode,'form': form,})
    elif language == "es":
        return render(request, "register_es.html", {"view_mode": view_mode,'form': form,})



# Dashboard view (requires login)
@login_required
def dashboard(request):
    """
    Displays the user dashboard with saved Spotify wraps.

    - Handles preference updates for view mode and language.
    - Queries the user's saved wraps for display.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered dashboard template.
    """
    # Handle POST requests for settings
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        # Query the user's saved wraps
        wraps = request.user.spotify_wraps.all()
        if language == "en":
            return render(request, "dashboard.html", {"view_mode": view_mode,"wraps": wraps})
        elif language == "de":
            return render(request, "dashboard_de.html", {"view_mode": view_mode,"wraps": wraps})
        elif language == "es":
            return render(request, "dashboard_es.html", {"view_mode": view_mode,"wraps": wraps})

    # Handle GET requests and retrieve current settings
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    # Query the user's saved wraps
    wraps = request.user.spotify_wraps.all()

    if language == "en":
        return render(request, "dashboard.html", {"view_mode": view_mode, "wraps": wraps})
    elif language == "de":
        return render(request, "dashboard_de.html", {"view_mode": view_mode, "wraps": wraps})
    elif language == "es":
        return render(request, "dashboard_es.html", {"view_mode": view_mode, "wraps": wraps})


def user_logout(request):
    """
        Logs the user out and redirects to the landing page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: A redirect to the landing page.
    """
    logout(request)
    return redirect('landing')

#Delete account
@login_required
def delete_account(request):
    """
        Deletes the currently authenticated user's account.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: A redirect to the landing page.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('landing')  # Redirect to the landing page or another desired page
    return render(request, 'delete_account.html')

# Spotify login view
def spotify_login(request):
    """
        Initiates Spotify OAuth authentication flow.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: A redirect to Spotify's authorization endpoint.
    """
    scope = 'user-top-read user-read-recently-played'
    spotify_auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
    return redirect(spotify_auth_url)

# Spotify callback view
def callback(request):
    """
        Handles the Spotify OAuth callback, exchanging the code for an access token.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: A redirect to the generate-wrap view or an error page.
        """
    code = request.GET.get('code')
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=token_data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        request.session['spotify_access_token'] = access_token
        return redirect('generate-wrap')  # Redirect to the updated wrap view
    else:
        return render(request, 'error.html', {'message': 'Spotify login failed.'})

def get_top_tracks(access_token, time_frame):
    top_tracks = []
    limit = 50
    offset = 0

    # Loop through to fetch all tracks, 50 at a time
    while True:
        url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_frame}&limit={limit}&offset={offset}'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        data = response.json()

        # If there are no more tracks to fetch, break the loop
        if not data.get('items'):
            break

        top_tracks.extend(data['items'])
        offset += limit  # Move to the next set of 50 tracks

    return top_tracks

# Generate the user's Spotify wrap
@login_required
def generate_wrap(request):
    """
        Generates the user's Spotify wrap based on their listening data.

        - Fetches top tracks, artists, and audio features using Spotify API.
        - Calculates listening patterns, genre breakdowns, and mood playlists.
        - Optionally saves the generated wrap to the database.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered wrap template or a redirect to Spotify login.
    """
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('spotify-login')

    # Get the time frame from GET request or default to 'short_term'
    time_frame = request.POST.get('time_frame', 'short_term')
    x = time_frame
    headers = {'Authorization': f'Bearer {access_token}'}
    view_mode = request.session.get("view_mode", "dark")
    language = request.session.get("language", "en")

    # Spotify API URLs with the selected time frame
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_frame}&limit=50'
    top_artists_url = f'https://api.spotify.com/v1/me/top/artists?time_range={time_frame}&limit=50'

    # Fetch tracks and artists based on time frame
    response_tracks = requests.get(top_tracks_url, headers=headers)
    response_artists = requests.get(top_artists_url, headers=headers)

    #set fetched data
    top_tracks = response_tracks.json().get('items', []) if response_tracks.status_code == 200 else []
    top_artists = response_artists.json().get('items', []) if response_artists.status_code == 200 else []
    #display limit to 5
    top_tracks_display = top_tracks[:3]
    top_artists_display = top_artists[:3]
    top_tracks_details = top_tracks[:5]
    top_artists_details = top_artists[:5]
    # Get track IDs from top tracks
    track_ids = [track['id'] for track in top_tracks]

    # Fetch audio features for the tracks
    audio_features_url = f'https://api.spotify.com/v1/audio-features?ids={",".join(track_ids)}'
    response_audio_features = requests.get(audio_features_url, headers=headers)
    audio_features = response_audio_features.json().get('audio_features', [])

    total_genres_played = 0

    for artist in top_artists:
        for genre in artist.get('genres', []):
            total_genres_played = total_genres_played + 1

    # Calculate genres
    genres = []
    for artist in top_artists:
        for genre in artist.get('genres', []):
            genres.append(genre)
    genre_counts = Counter(genres)
    favorite_genres = [genre for genre, _ in genre_counts.most_common(5)]

    # Extract albums from top tracks
    top_albums = [
        {
            'name': track['album']['name'],
            'artist': track['album']['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        for track in top_tracks[:3]
    ]

    # Initialize mood playlists
    mood_playlists = {
        'chill_vibes': [],
        'workout_hits': [],
        'study_tunes': []
    }

    # Categorize tracks based on multiple audio features
    for track, features in zip(top_tracks_display[:3], audio_features):
        # Ensure the feature is available
        if features and all(key in features for key in ['energy', 'danceability', 'valence']):
            energy = features['energy']
            danceability = features['danceability']
            valence = features['valence']

            # Categorize based on energy, danceability, and valence
            if energy < 0.4 and valence < 0.5:
                mood_playlists['chill_vibes'].append(track)
            elif danceability > 0.7 and energy > 0.6:
                mood_playlists['workout_hits'].append(track)
            elif energy > 0.4 and energy < 0.7 and valence > 0.5:
                mood_playlists['study_tunes'].append(track)

    # Analyze listening patterns from recently played tracks
    recently_played_url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    response_recent = requests.get(recently_played_url, headers=headers)
    recently_played = response_recent.json().get('items', []) if response_recent.status_code == 200 else []

    #analyze the listening times throughout the day for the bar graph
    def analyze_listening_patterns(recently_played):
        """
            Analyzes listening patterns from recently played tracks.

            Args:
                recently_played (list): A list of recently played track data.

            Returns:
                dict: The analyzed listening patterns by time of day.
        """
        patterns = {
            'time_of_day': {
                'morning': 0,
                'afternoon': 0,
                'evening': 0,
                'night': 0,
            },
        }

        for item in recently_played:
            played_at_raw = item['played_at']  # Raw timestamp with fractional seconds
            played_at = datetime.strptime(played_at_raw.split('.')[0],
                                          "%Y-%m-%dT%H:%M:%S")  # Remove fractional seconds and parse
            hour = played_at.hour

            # Time of day
            if 5 <= hour < 12:
                patterns['time_of_day']['morning'] += 1
            elif 12 <= hour < 17:
                patterns['time_of_day']['afternoon'] += 1
            elif 17 <= hour < 22:
                patterns['time_of_day']['evening'] += 1
            else:
                patterns['time_of_day']['night'] += 1

        total = sum(patterns['time_of_day'].values())
        if total > 0:
            for key in patterns['time_of_day']:
                patterns['time_of_day'][key] = round((patterns['time_of_day'][key] / total) * 100, 2)

        return patterns

    #analyze the genre breakdowns for graphs
    def analyze_genres(top_artists):
        """
            Analyzes genre data from top artists.

            Args:
                top_artists (list): A list of top artist data.

            Returns:
                dict: A dictionary of genre counts.
        """
        genre_counts_graph = {}

        for artist in top_artists:
            for genre in artist.get('genres', []):
                genre_counts_graph[genre] = genre_counts_graph.get(genre, 0) + 1

        # Sort by frequency and return the top 5 genres
        sorted_genres = sorted(genre_counts_graph.items(), key=lambda x: x[1], reverse=True)[:5]
        return dict(sorted_genres)

    # Analyze longest track streaks
    def get_longest_streaks(recently_played):
        """
            Calculates the longest track streaks from recently played data.

            Args:
                recently_played (list): A list of recently played track data.

            Returns:
                list: The top 3 longest track streaks.
        """
        streaks = defaultdict(int)  # Track streaks per song
        longest_streaks = []  # Final list of longest streaks

        if not recently_played:
            return []

        last_track_id = None
        current_streak_count = 0

        for item in recently_played:
            track = item['track']
            track_id = track['id']
            track_name = track['name']

            if track_id == last_track_id:
                current_streak_count += 1
            else:
                if last_track_id:
                    # Save streak for the previous track
                    streaks[last_track_id] = max(streaks[last_track_id], current_streak_count)
                last_track_id = track_id
                current_streak_count = 1

        # Ensure the final track's streak is saved
        if last_track_id:
            streaks[last_track_id] = max(streaks[last_track_id], current_streak_count)

        # Sort streaks by length (descending) and return top 3 streaks
        sorted_streaks = sorted(streaks.items(), key=lambda x: x[1], reverse=True)[:3]
        for track_id, streak_count in sorted_streaks:
            track_data = next((item['track'] for item in recently_played if item['track']['id'] == track_id), None)
            if track_data:
                # Get album artwork URL
                album_art_url = track_data['album']['images'][1]['url'] if 'images' in track_data['album'] else None
                longest_streaks.append({
                    'name': track_data['name'],
                    'streak': streak_count,
                    'album_art_url': album_art_url  # Add album art URL here
                })

        return longest_streaks

    #listening patterns and genre breakdown called
    listening_patterns = analyze_listening_patterns(recently_played)
    genre_breakdown = analyze_genres(top_artists)

    # Call the function to calculate streaks
    longest_streaks = get_longest_streaks(recently_played)
    total_songs_played = len(top_tracks)

    # Metric 3: Total Listening Time (in hours)
    total_duration_ms = sum(track['duration_ms'] for track in top_tracks)
    total_duration_minutes = round(total_duration_ms / (1000 * 60), 2)  # Convert ms to minutes

    # Save the wrap if requested
    wrap_name = f"Top Tracks - {time_frame.replace('_', ' ').title()}"
    if request.method == 'POST' and 'save_wrap' in request.POST:
        time_frame = request.POST.get('time_frame', 'short_term')  # Use the time_frame from the form
        wrap = SpotifyWrap.objects.create(
            user=request.user,
            time_frame=time_frame,  # This ensures the selected time frame is correctly saved
            created_at=datetime.now(),
            data={
                'wrap_name': wrap_name,
                'time_frame': time_frame,
                'top_tracks': top_tracks_details,
                'top_artists': top_artists_details,
                'favorite_genres': favorite_genres,
                'top_albums': top_albums,
                'longest_streaks': longest_streaks,
                'total_songs_played': total_songs_played,  # Total number of songs played
                'total_duration_minutes': total_duration_minutes,  # Total listening time in minutes
                'total_genres_played': total_genres_played,  # Total number of genres played
                'listening_patterns': listening_patterns,  # The time-of-day patterns
                'genre_breakdown': genre_breakdown,  # Detailed genre breakdown (if needed for charts)
                "view_mode": view_mode,
                "language": language
            }
        )
        # Redirect back to the dashboard after saving
        return redirect('dashboard')

    context = {  # Ensure wrap is passed correctly
        'time_frame': time_frame,
        'top_tracks': top_tracks_display,
        'top_artists': top_artists_display,
        'favorite_genres': favorite_genres,
        'top_albums': top_albums,
        'listening_patterns': listening_patterns,
        'genre_breakdown': genre_breakdown,
        'mood_playlists': mood_playlists,
        'longest_streaks': longest_streaks,
        'total_songs_played': total_songs_played,
        'total_genres_played': total_genres_played,
        'total_duration_minutes': total_duration_minutes,
        "view_mode": view_mode,
        "language": language
    }

    if language == "en":
        return render(request, "wrapper.html", context)
    elif language == "de":
        return render(request, "wrapper_de.html", context)
    elif language == "es":
        return render(request, "wrapper_es.html", context)

@login_required
def save_wrap(request):
    if request.method == 'POST':
        access_token = request.session.get('spotify_access_token')
        if not access_token:
            return JsonResponse({'error': 'Spotify access token is missing.'}, status=400)

        time_frame = request.POST.get('time_frame', 'short_term')
        top_tracks = request.POST.get('top_tracks', [])
        top_artists = request.POST.get('top_artists', [])

        wrap = SpotifyWrap.objects.create(
            user=request.user,
            time_frame=time_frame,
            created_at=datetime.now(),
            data={
                'top_tracks': top_tracks,
                'top_artists': top_artists,
            }
        )
        wrap.save()
        return JsonResponse({'success': True, 'message': 'Wrap saved successfully!'})

# About page view
def about(request):
    """"
    Renders the About page with support for view mode and language preferences.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered About page template.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        if language == "en":
            return render(request, "about.html", {"view_mode": view_mode})
        elif language == "de":
            return render(request, "about_de.html", {"view_mode": view_mode})
        elif language == "es":
            return render(request, "about_es.html", {"view_mode": view_mode})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    if language == "en":
        return render(request, "about.html", {"view_mode": view_mode})
    elif language == "de":
        return render(request, "about_de.html", {"view_mode": view_mode})
    elif language == "es":
        return render(request, "about_es.html", {"view_mode": view_mode})

# wrap features and attributes views go below
def get_user_top_tracks(access_token):
    """
        Fetches the user's top tracks from Spotify.

        Args:
            access_token (str): The Spotify API access token.

        Returns:
            list: The user's top tracks or None if the request fails.
    """
    url = 'https://api.spotify.com/v1/me/top/tracks?limit=10'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['items']
    else:
        return None

@login_required
def wrap_detail(request, wrap_id):
    """
        Displays the details of a specific Spotify wrap.

        - Handles updates to view mode and language preferences.
        - Retrieves wrap details for display.

        Args:
            request (HttpRequest): The HTTP request object.
            wrap_id (int): The ID of the wrap to display.

        Returns:
            HttpResponse: The rendered wrap detail template.
    """
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)

    if request.method == "POST":
        # Handle settings update
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        # Context for rendering after POST
        context = {
            'wrap': wrap,
            'top_tracks': wrap.data.get('top_tracks', []),
            'top_artists': wrap.data.get('top_artists', []),
            "view_mode": view_mode,
            "language": language,
        }
        if language == "en":
            return render(request, "wrap_detail.html", context)
        elif language == "de":
            return render(request, "wrap_detail_de.html", context)
        elif language == "es":
            return render(request, "wrap_detail_es.html", context)

    # Retrieve session data for GET requests
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    # Context for rendering in GET requests
    context = {
        'wrap': wrap,
        'top_tracks': wrap.data.get('top_tracks', []),
        'top_artists': wrap.data.get('top_artists', []),
        "view_mode": view_mode,
        "language": language,
    }

    if language == "en":
        return render(request, "wrap_detail.html", context)
    elif language == "de":
        return render(request, "wrap_detail_de.html", context)
    elif language == "es":
        return render(request, "wrap_detail_es.html", context)


def index(request):
    return render(request, 'index.html')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('landing')  # Redirect to the landing page or another desired page
    return render(request, 'delete_account.html')

def user_settings(request):
    """
        Renders the user settings page with support for view mode and language preferences.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The rendered user settings template.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        if language == "en":
            return render(request, "user_settings.html", {"view_mode": view_mode})
        elif language == "de":
            return render(request, "user_settings_de.html", {"view_mode": view_mode})
        elif language == "es":
            return render(request, "user_settings_es.html", {"view_mode": view_mode})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    if language == "en":
        return render(request, "user_settings.html", {"view_mode": view_mode})
    elif language == "de":
        return render(request, "user_settings_de.html", {"view_mode": view_mode})
    elif language == "es":
        return render(request, "user_settings_es.html", {"view_mode": view_mode})


@login_required
def delete_wrap(request, wrap_id):
    """
        Deletes a specific Spotify wrap.

        Args:
            request (HttpRequest): The HTTP request object.
            wrap_id (int): The ID of the wrap to delete.

        Returns:
            HttpResponse: A redirect to the dashboard.
    """
    # Find the wrap for the current user
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)

    if request.method == 'POST':
        # Delete the wrap
        wrap.delete()
        messages.success(request, 'Wrap deleted successfully.')
        return redirect('dashboard')  # Redirect to dashboard after deletion

    return redirect('dashboard')  # If not a POST request, redirect back to dashboard

def share_wrap(request, share_token):
    # Get the wrap using the share_token
    wrap = get_object_or_404(SpotifyWrap, share_token=share_token)

    # Context data to pass to the template
    context = {
        'wrap': wrap,
    }

    return render(request, 'shared_wrap.html', context)

@login_required
def share_view(request, share_token):
    # Get the wrap object using the share_token
    wrap = get_object_or_404(Wrap, share_token=share_token)

    # Generate the share URL dynamically
    share_url = request.build_absolute_uri(f'/wrap/share/{wrap.share_token}/')

    # Create a title and summary for the LinkedIn post
    title = f"Check out {wrap.user.username}'s Wrap!"
    summary = f"Check out {wrap.user.username}'s wrap! See the cool stats and details."

    # Pass all the necessary data to the template
    return render(request, 'share_view.html', {
        'wrap': wrap,
        'share_url': share_url,
        'title': title,
        'summary': summary,
    })
