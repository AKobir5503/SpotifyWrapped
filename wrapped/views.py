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


# use the settings instead of hardcoded values
SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

SPOTIFY_REDIRECT_URI = 'http://localhost:8000/callback/'

# Landing page view
def landing(request):
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "landing.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "landing.html", {"view_mode": view_mode, "language": language})

# Login view
def login_user(request):
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
                },
            )

    # Retrieve view mode and language settings from the session
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "login.html", {"view_mode": view_mode, "language": language})

# Register user view
def register_user(request):
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

    return render(request, 'register.html', {
        'form': form,
        'view_mode': view_mode,
        'language': language
    })


# Dashboard view (requires login)
@login_required
def dashboard(request):
    # Handle POST requests for settings
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        # Query the user's saved wraps
        wraps = request.user.spotify_wraps.all()
        return render(
            request,
            "dashboard.html",
            {"wraps": wraps, "view_mode": view_mode, "language": language},
        )

    # Handle GET requests and retrieve current settings
    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    # Query the user's saved wraps
    wraps = request.user.spotify_wraps.all()

    return render(
        request,
        "dashboard.html",
        {"wraps": wraps, "view_mode": view_mode, "language": language},
    )


def user_logout(request):
    logout(request)
    return redirect('landing')

#Delete account
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('landing')  # Redirect to the landing page or another desired page
    return render(request, 'delete_account.html')

# Spotify login view
def spotify_login(request):
    scope = 'user-top-read user-read-recently-played'
    spotify_auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
    return redirect(spotify_auth_url)

# Spotify callback view
def callback(request):
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
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('spotify-login')

    # Get the time frame from GET request or default to 'short_term'
    time_frame = request.POST.get('time_frame', 'short_term')
    x = time_frame
    headers = {'Authorization': f'Bearer {access_token}'}

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
    top_tracks_display = top_tracks[:5]
    top_artists_display = top_artists[:5]
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
        for track in top_tracks[:5]
    ]

    # Initialize mood playlists
    mood_playlists = {
        'chill_vibes': [],
        'workout_hits': [],
        'study_tunes': []
    }

    # Categorize tracks based on multiple audio features
    for track, features in zip(top_tracks_display[:5], audio_features):
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
        """Analyze listening patterns from recently played tracks."""
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
        """Analyze genres from the top artists."""
        genre_counts_graph = {}

        for artist in top_artists:
            for genre in artist.get('genres', []):
                genre_counts_graph[genre] = genre_counts_graph.get(genre, 0) + 1

        # Sort by frequency and return the top 5 genres
        sorted_genres = sorted(genre_counts_graph.items(), key=lambda x: x[1], reverse=True)[:5]
        return dict(sorted_genres)

    def get_longest_streaks(recently_played):
        """Calculate the longest track streaks from recently played data."""
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
                'top_tracks': top_tracks,
                'top_artists': top_artists,
                'favorite_genres': favorite_genres,
                'top_albums': top_albums,
                'longest_streaks': longest_streaks,
                'total_songs_played': total_songs_played,  # Total number of songs played
                'total_duration_minutes': total_duration_minutes,  # Total listening time in minutes
                'total_genres_played': total_genres_played,  # Total number of genres played
                'listening_patterns': listening_patterns,  # The time-of-day patterns
                'genre_breakdown': genre_breakdown,  # Detailed genre breakdown (if needed for charts)
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
    }
    return render(request, 'wrapper.html', context)

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
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "about.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "about.html", {"view_mode": view_mode, "language": language})

# wrap features and attributes views go below
def get_user_top_tracks(access_token):
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
        return render(request, 'wrap_detail.html', context)

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
    return render(request, 'wrap_detail.html', context)

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
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        # Save the settings to the session
        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "user_settings.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "user_settings.html", {"view_mode": view_mode, "language": language})

@login_required
def delete_wrap(request, wrap_id):
    # Find the wrap for the current user
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)

    if request.method == 'POST':
        # Delete the wrap
        wrap.delete()
        messages.success(request, 'Wrap deleted successfully.')
        return redirect('dashboard')  # Redirect to dashboard after deletion

    return redirect('dashboard')  # If not a POST request, redirect back to dashboard

