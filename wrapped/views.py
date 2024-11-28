
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
from django.contrib.auth.models import User
from django.contrib import messages


# Spotify API credentials
SPOTIFY_CLIENT_ID = '46e8f14a666f47ddb347507b8a00816a'
SPOTIFY_CLIENT_SECRET = 'ed5ff1725aef41f4b3d75c72aa659417'
SPOTIFY_REDIRECT_URI = 'http://localhost:8000/callback/'

# Landing page view
def landing(request):
    return render(request, 'landing.html')

# Login view
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to user dashboard
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

# Register user view
def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

# Dashboard view (requires login)
@login_required
def dashboard(request):
    # Query the user's saved wraps
    wraps = request.user.spotify_wraps.all()  # Make sure the related name is correct
    return render(request, 'dashboard.html', {'wraps': wraps})

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

# Generate the user's Spotify wrap
@login_required
def generate_wrap(request):
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('spotify-login')

    # Get the time frame from GET request or default to 'short_term'
    time_frame = request.POST.get('time_frame', 'short_term')

    headers = {'Authorization': f'Bearer {access_token}'}

    # Spotify API URLs with the selected time frame
    top_tracks_url = f'https://api.spotify.com/v1/me/top/tracks?time_range={time_frame}&limit=10'
    top_artists_url = f'https://api.spotify.com/v1/me/top/artists?time_range={time_frame}&limit=10'

    # Fetch tracks and artists
    response_tracks = requests.get(top_tracks_url, headers=headers)
    top_tracks = response_tracks.json().get('items', []) if response_tracks.status_code == 200 else []

    response_artists = requests.get(top_artists_url, headers=headers)
    top_artists = response_artists.json().get('items', []) if response_artists.status_code == 200 else []

    # Calculate genres
    genres = []
    for artist in top_artists:
        genres.extend(artist.get('genres', []))
    genre_counts = Counter(genres)
    favorite_genres = [genre for genre, _ in genre_counts.most_common(5)]

    # Extract albums from top tracks
    top_albums = [
        {
            'name': track['album']['name'],
            'artist': track['album']['artists'][0]['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        for track in top_tracks
    ]

    # Longest track streaks (Mock data for now, you can implement a real logic if Spotify provides listening history)
    longest_streaks = [
        {'name': track['name'], 'streak': random.randint(2, 10)} for track in top_tracks[:3]
    ]

    # Fetch lyrics (Mock for now, integrate lyrics API if desired)
    top_lyrics = [
        {
            'name': track['name'],
            'lyrics': "Sample lyric snippet for demonstration purposes."
        }
        for track in top_tracks[:3]
    ]

    # Save the wrap if requested
    wrap_name = f"Top Tracks - {time_frame.replace('_', ' ').title()}"
    if request.method == 'POST' and 'save_wrap' in request.POST:
        wrap = SpotifyWrap.objects.create(
            user=request.user,
            time_frame=time_frame,
            created_at=datetime.now(),
            data={
                'top_tracks': top_tracks,
                'top_artists': top_artists,
                'favorite_genres': favorite_genres,
                'top_albums': top_albums,
                'longest_streaks': longest_streaks,
                'top_lyrics': top_lyrics,
            }
        )
        wrap.save()
        return redirect('dashboard')  # Redirect back to dashboard after saving

    context = {
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'favorite_genres': favorite_genres,
        'top_albums': top_albums,
        'longest_streaks': longest_streaks,
        'top_lyrics': top_lyrics,
        'time_frame': time_frame,
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
    return render(request, 'about.html')

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

    # If you want to pass data from the wrap (e.g., top tracks, top artists, etc.)
    context = {
        'wrap': wrap,
        'top_tracks': wrap.data.get('top_tracks', []),
        'top_artists': wrap.data.get('top_artists', []),
    }
    return render(request, 'wrap_detail.html', context)

def index(request):
    return render(request, 'index.html')

def settings(request):
    return render(request, 'settings.html')
