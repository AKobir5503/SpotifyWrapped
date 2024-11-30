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
from django.contrib.auth.models import User
from django.contrib import messages
from collections import defaultdict

# Use the settings instead of hardcoded values
SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/callback/'

def landing(request):
    """
    Handles the landing page for the application.

    - Saves view mode and language preferences to the session on POST requests.
    - Displays the landing page with user-specific preferences retrieved from the session.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered landing page with the user's view mode and language preferences.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "landing.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "landing.html", {"view_mode": view_mode, "language": language})

def login_user(request):
    """
    Handles user login.

    - Authenticates the user with username and password.
    - Saves view mode and language preferences to the session.
    - Redirects to the dashboard if login is successful or re-renders the login page with an error.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered login page or redirect to the dashboard upon successful login.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
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

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "login.html", {"view_mode": view_mode, "language": language})

def register_user(request):
    """
    Handles user registration.

    - Displays a registration form.
    - Creates a new user and redirects to the login page upon successful form submission.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered registration form or redirect to login page on successful registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    """
    Displays the user's dashboard with their saved Spotify wraps.

    - Retrieves user-specific preferences and saved wraps.
    - Updates session preferences on POST requests.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered dashboard page with wraps and user-specific settings.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        wraps = request.user.spotify_wraps.all()
        return render(
            request,
            "dashboard.html",
            {"wraps": wraps, "view_mode": view_mode, "language": language},
        )

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")
    wraps = request.user.spotify_wraps.all()

    return render(
        request,
        "dashboard.html",
        {"wraps": wraps, "view_mode": view_mode, "language": language},
    )

def user_logout(request):
    """
    Logs out the current user and redirects to the landing page.

    Args:
        request: The HTTP request object.

    Returns:
        Redirect to the landing page.
    """
    logout(request)
    return redirect('landing')

@login_required
def delete_account(request):
    """
    Deletes the logged-in user's account.

    - Confirms deletion via a POST request.
    - Displays a success message and redirects to the landing page.

    Args:
        request: The HTTP request object.

    Returns:
        Redirect to the landing page after account deletion.
    """
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, "Your account has been successfully deleted.")
        return redirect('landing')

    return render(request, 'delete_account.html')

def spotify_login(request):
    """
    Redirects the user to Spotify's authorization page.

    Args:
        request: The HTTP request object.

    Returns:
        Redirect to Spotify's authorization URL.
    """
    scope = 'user-top-read user-read-recently-played'
    spotify_auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
    return redirect(spotify_auth_url)

def callback(request):
    """
    Handles the callback from Spotify after user authorization.

    - Exchanges the authorization code for an access token.
    - Saves the access token in the session.

    Args:
        request: The HTTP request object.

    Returns:
        Redirect to the Spotify wrap generation view or an error page.
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
        return redirect('generate-wrap')
    else:
        return render(request, 'error.html', {'message': 'Spotify login failed.'})

def get_top_tracks(access_token, time_frame):
    """
    Fetches the top tracks for the user from Spotify.

    Args:
        access_token: Spotify API access token.
        time_frame: Time frame for top tracks (e.g., short_term, medium_term, long_term).

    Returns:
        List of top tracks for the specified time frame.
    """
    top_tracks = []
    limit = 50
    offset = 0

    while True:
        url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_frame}&limit={limit}&offset={offset}'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(url, headers=headers)
        data = response.json()

        if not data.get('items'):
            break

        top_tracks.extend(data['items'])
        offset += limit

    return top_tracks

@login_required
def generate_wrap(request):
    """
    Generates a Spotify wrap for the logged-in user.

    - Fetches Spotify user data (top tracks, artists, and audio features).
    - Categorizes data into mood playlists.
    - Analyzes listening patterns and genre breakdowns.
    - Provides options to save the generated wrap.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered wrap generation page with the generated Spotify wrap details.
    """
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('spotify-login')

    # Get the time frame from POST request or default to 'short_term'
    time_frame = request.POST.get('time_frame', 'short_term')
    headers = {'Authorization': f'Bearer {access_token}'}

    # Spotify API URLs with the selected time frame
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_frame}&limit=50'
    top_artists_url = f'https://api.spotify.com/v1/me/top/artists?time_range={time_frame}&limit=50'

    # Fetch tracks and artists data
    response_tracks = requests.get(top_tracks_url, headers=headers)
    response_artists = requests.get(top_artists_url, headers=headers)

    # Set fetched data
    top_tracks = response_tracks.json().get('items', []) if response_tracks.status_code == 200 else []
    top_artists = response_artists.json().get('items', []) if response_artists.status_code == 200 else []

    # Display a limited number of tracks and artists
    top_tracks_display = top_tracks[:5]
    top_artists_display = top_artists[:5]

    # Prepare data for mood playlists
    track_ids = [track['id'] for track in top_tracks]
    audio_features_url = f'https://api.spotify.com/v1/audio-features?ids={",".join(track_ids)}'
    response_audio_features = requests.get(audio_features_url, headers=headers)
    audio_features = response_audio_features.json().get('audio_features', [])

    mood_playlists = {
        'chill_vibes': [],
        'workout_hits': [],
        'study_tunes': []
    }

    for track, features in zip(top_tracks_display, audio_features):
        if features and all(key in features for key in ['energy', 'danceability', 'valence']):
            energy = features['energy']
            danceability = features['danceability']
            valence = features['valence']

            if energy < 0.4 and valence < 0.5:
                mood_playlists['chill_vibes'].append(track)
            elif danceability > 0.7 and energy > 0.6:
                mood_playlists['workout_hits'].append(track)
            elif 0.4 <= energy <= 0.7 and valence > 0.5:
                mood_playlists['study_tunes'].append(track)

    # Analyze genres
    genres = []
    for artist in top_artists:
        genres.extend(artist.get('genres', []))
    genre_counts = Counter(genres)
    favorite_genres = [genre for genre, _ in genre_counts.most_common(5)]

    # Prepare albums data
    top_albums = [
        {
            'name': track['album']['name'],
            'artist': track['album']['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        for track in top_tracks[:5]
    ]

    # Analyze listening patterns
    recently_played_url = 'https://api.spotify.com/v1/me/player/recently-played?limit=50'
    response_recent = requests.get(recently_played_url, headers=headers)
    recently_played = response_recent.json().get('items', []) if response_recent.status_code == 200 else []

    def analyze_listening_patterns(recently_played):
        patterns = {
            'time_of_day': {
                'morning': 0,
                'afternoon': 0,
                'evening': 0,
                'night': 0,
            },
        }

        for item in recently_played:
            played_at_raw = item['played_at']
            played_at = datetime.strptime(played_at_raw.split('.')[0], "%Y-%m-%dT%H:%M:%S")
            hour = played_at.hour

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

    listening_patterns = analyze_listening_patterns(recently_played)

    def analyze_genres(top_artists):
        genre_counts_graph = {}
        for artist in top_artists:
            for genre in artist.get('genres', []):
                genre_counts_graph[genre] = genre_counts_graph.get(genre, 0) + 1

        sorted_genres = sorted(genre_counts_graph.items(), key=lambda x: x[1], reverse=True)[:5]
        return dict(sorted_genres)

    genre_breakdown = analyze_genres(top_artists)

    def get_longest_streaks(recently_played):
        streaks = defaultdict(int)
        longest_streaks = []

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
                    streaks[last_track_id] = max(streaks[last_track_id], current_streak_count)
                last_track_id = track_id
                current_streak_count = 1

        if last_track_id:
            streaks[last_track_id] = max(streaks[last_track_id], current_streak_count)

        sorted_streaks = sorted(streaks.items(), key=lambda x: x[1], reverse=True)[:3]
        for track_id, streak_count in sorted_streaks:
            track_data = next((item['track'] for item in recently_played if item['track']['id'] == track_id), None)
            if track_data:
                longest_streaks.append({
                    'name': track_data['name'],
                    'streak': streak_count
                })

        return longest_streaks

    longest_streaks = get_longest_streaks(recently_played)

    total_duration_ms = sum(track['duration_ms'] for track in top_tracks)
    total_duration_minutes = round(total_duration_ms / (1000 * 60), 2)

    wrap_name = f"Top Tracks - {time_frame.replace('_', ' ').title()}"
    if request.method == 'POST' and 'save_wrap' in request.POST:
        time_frame = request.POST.get('time_frame', 'short_term')
        wrap = SpotifyWrap.objects.create(
            user=request.user,
            time_frame=time_frame,
            created_at=datetime.now(),
            data={
                'wrap_name': wrap_name,
                'time_frame': time_frame,
                'top_tracks': top_tracks,
                'top_artists': top_artists,
                'favorite_genres': favorite_genres,
                'top_albums': top_albums,
                'longest_streaks': longest_streaks,
                'total_duration_minutes': total_duration_minutes,
                'listening_patterns': listening_patterns,
                'genre_breakdown': genre_breakdown,
            }
        )
        return redirect('dashboard')

    context = {
        'time_frame': time_frame,
        'top_tracks': top_tracks_display,
        'top_artists': top_artists_display,
        'favorite_genres': favorite_genres,
        'top_albums': top_albums,
        'listening_patterns': listening_patterns,
        'genre_breakdown': genre_breakdown,
        'mood_playlists': mood_playlists,
        'longest_streaks': longest_streaks,
        'total_duration_minutes': total_duration_minutes,
    }
    return render(request, 'wrapper.html', context)


@login_required
def save_wrap(request):
    """
    Saves a Spotify wrap for the logged-in user.

    - Creates a new SpotifyWrap object with data submitted via POST request.

    Args:
        request: The HTTP request object.

    Returns:
        JSON response indicating success or error.
    """
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

def about(request):
    """
    Displays the about page for the application.

    - Saves view mode and language preferences to the session on POST requests.
    - Renders the about page with user-specific preferences.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered about page with the user's view mode and language preferences.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "about.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "about.html", {"view_mode": view_mode, "language": language})

def get_user_top_tracks(access_token):
    """
    Fetches the top 10 tracks for the user from Spotify.

    Args:
        access_token: Spotify API access token.

    Returns:
        List of the user's top 10 tracks, or None if the request fails.
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

    - Handles POST requests to update view mode and language preferences.
    - Retrieves the wrap details for rendering.

    Args:
        request: The HTTP request object.
        wrap_id: ID of the SpotifyWrap object to retrieve.

    Returns:
        Rendered wrap detail page with the wrap data and user-specific settings.
    """
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id)

    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        context = {
            'wrap': wrap,
            'top_tracks': wrap.data.get('top_tracks', []),
            'top_artists': wrap.data.get('top_artists', []),
            "view_mode": view_mode,
            "language": language,
        }
        return render(request, 'wrap_detail.html', context)

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    context = {
        'wrap': wrap,
        'top_tracks': wrap.data.get('top_tracks', []),
        'top_artists': wrap.data.get('top_artists', []),
        "view_mode": view_mode,
        "language": language,
    }
    return render(request, 'wrap_detail.html', context)

def index(request):
    """
    Displays the application's home page.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered index page.
    """
    return render(request, 'index.html')

@login_required
def delete_wrap(request, wrap_id):
    """
    Deletes a specific Spotify wrap for the logged-in user.

    - Finds the wrap belonging to the user and deletes it.
    - Redirects to the dashboard after deletion.

    Args:
        request: The HTTP request object.
        wrap_id: ID of the SpotifyWrap object to delete.

    Returns:
        Redirect to the dashboard page.
    """
    wrap = get_object_or_404(SpotifyWrap, id=wrap_id, user=request.user)

    if request.method == 'POST':
        wrap.delete()
        messages.success(request, 'Wrap deleted successfully.')
        return redirect('dashboard')

    return redirect('dashboard')

def user_settings(request):
    """
    Manages user-specific settings for the application.

    - Saves view mode and language preferences to the session on POST requests.
    - Renders the settings page with the current preferences.

    Args:
        request: The HTTP request object.

    Returns:
        Rendered settings page with the user's view mode and language preferences.
    """
    if request.method == "POST":
        view_mode = request.POST.get("view_mode", "light")
        language = request.POST.get("language", "en")

        request.session["view_mode"] = view_mode
        request.session["language"] = language

        return render(request, "user_settings.html", {"view_mode": view_mode, "language": language})

    view_mode = request.session.get("view_mode", "light")
    language = request.session.get("language", "en")

    return render(request, "user_settings.html", {"view_mode": view_mode, "language": language})

