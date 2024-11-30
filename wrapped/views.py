import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from collections import Counter
from datetime import datetime

# Spotify credentials from settings
SPOTIFY_CLIENT_ID = settings.SPOTIFY_CLIENT_ID
SPOTIFY_CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET
SPOTIFY_REDIRECT_URI = settings.SPOTIFY_REDIRECT_URI

def spotify_login(request):
    """
    Redirect user to Spotify login page.
    """
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return render(request, 'error.html', {
            'message': 'Spotify client credentials are not configured.'
        })

    scope = 'user-top-read user-read-recently-played'
    spotify_auth_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={SPOTIFY_REDIRECT_URI}&scope={scope}"
    )
    return redirect(spotify_auth_url)

def callback(request):
    """
    Handle Spotify's callback and exchange code for an access token.
    """
    code = request.GET.get('code')
    if not code:
        return render(request, 'error.html', {'message': 'Authorization failed. No code provided.'})

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
        request.session['spotify_access_token'] = tokens.get('access_token')
        return redirect('dashboard')
    else:
        return render(request, 'error.html', {'message': 'Failed to authenticate with Spotify.'})

@login_required
def dashboard(request):
    """
    User dashboard displaying Spotify data.
    """
    access_token = request.session.get('spotify_access_token')
    if not access_token:
        return redirect('spotify-login')

    headers = {'Authorization': f'Bearer {access_token}'}
    top_tracks_url = 'https://api.spotify.com/v1/me/top/tracks?limit=5'
    response = requests.get(top_tracks_url, headers=headers)

    if response.status_code == 200:
        top_tracks = response.json().get('items', [])
    else:
        top_tracks = []

    return render(request, 'dashboard.html', {'top_tracks': top_tracks})