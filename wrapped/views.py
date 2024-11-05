from django.contrib.sites import requests
from django.shortcuts import redirect, render
from urllib.parse import urlencode
import requests
from django.urls import reverse
from collections import Counter


# Spotify API credentials
CLIENT_ID = '46e8f14a666f47ddb347507b8a00816a'
CLIENT_SECRET = 'ed5ff1725aef41f4b3d75c72aa659417'
REDIRECT_URI = 'http://localhost:8000/callback/'

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def login(request):
    # Spotify authorization URL
    auth_url = 'https://accounts.spotify.com/authorize'
    scope = 'user-read-private user-read-email user-top-read'
    query_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
    }
    return redirect(f"{auth_url}?{urlencode(query_params)}")

def callback(request):
    # Get the authorization code from the callback URL
    code = request.GET.get('code')
    if not code:
        return redirect('login')  # Redirect to login if no code

    # Exchange the code for an access token
    token_url = 'https://accounts.spotify.com/api/token'
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    response = requests.post(token_url, data=token_data)
    token_info = response.json()

    # Store the access token in the session
    request.session['access_token'] = token_info.get('access_token')
    return redirect(reverse('wrapper'))

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
def logout(request):
    request.session.flush()
    return render(request, 'index.html')
