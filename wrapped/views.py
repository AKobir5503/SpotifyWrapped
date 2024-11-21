from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import requests
from django.contrib.auth import logout
from .models import SpotifyWrap

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
    # Use the correct related name: spotifywrap_set
    wraps = request.user.spotifywrap_set.all()
    return render(request, 'dashboard.html', {'wraps': wraps})

def user_logout(request):
    logout(request)
    return redirect('landing')


# Spotify login view
def spotify_login(request):
    scope = 'user-top-read user-read-recently-played'
    spotify_auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
    return redirect(spotify_auth_url)

# Spotify callback view
def spotify_callback(request):
    # Handle the callback from Spotify
    code = request.GET.get('code')
    if code:
        # Exchange the code for an access token
        token_url = 'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }
        response = requests.post(token_url, data=data)
        response_data = response.json()
        access_token = response_data.get('access_token')

        # Store the token in the session or the database
        request.session['spotify_token'] = access_token

        return redirect('dashboard')  # Redirect back to the dashboard page
    return redirect('login')  # In case something goes wrong, redirect to login page

# Generate the user's Spotify wrap
@login_required
def generate_wrap(request):
    # Fetch user’s top data from Spotify API
    top_tracks = get_user_top_tracks(request.session['spotify_access_token'])
    top_artists = get_user_top_artists(request.session['spotify_access_token'])
    top_genres = get_user_top_genres(request.session['spotify_access_token'])

    # Store this data in the database
    wrap = SpotifyWrap.objects.create(
        user=request.user,
        top_tracks=top_tracks,
        top_artists=top_artists,
        top_genres=top_genres,
    )

    # Redirect to the wrap view page
    return redirect('wrap_detail', wrap_id=wrap.id)

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

def wrap_detail(request, wrap_id):
    wrap = SpotifyWrap.objects.get(id=wrap_id)

    return render(request, 'wrap_detail.html', {'wrap': wrap})


def wrapper(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('login')

    # Fetch top tracks and top artists
    top_tracks_response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=5',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    top_artists_response = requests.get(
        'https://api.spotify.com/v1/me/top/artists?time_range=short_term&limit=5',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    # Process responses for tracks and artists
    if top_tracks_response.status_code == 200:
        top_tracks = top_tracks_response.json().get('items', [])
    else:
        top_tracks = []

    if top_artists_response.status_code == 200:
        top_artists = top_artists_response.json().get('items', [])
    else:
        top_artists = []

    # Extract genres from top artists
    genres = []
    for artist in top_artists:
        genres.extend(artist.get('genres', []))

    # Count occurrences of each genre and get the most common ones
    genre_counts = Counter(genres)
    favorite_genres = [genre for genre, count in genre_counts.most_common(5)]  # Top 5 genres

    context = {
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'favorite_genres': favorite_genres,
    }

    return render(request, 'wrapper.html', context)

def index(request):
    return render(request, 'index.html')