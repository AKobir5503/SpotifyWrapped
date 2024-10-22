import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.conf import settings
from urllib.parse import urlencode

# Spotify API credentials
CLIENT_ID = '46e8f14a666f47ddb347507b8a00816a'
CLIENT_SECRET = 'ed5ff1725aef41f4b3d75c72aa659417'
REDIRECT_URI = 'http://localhost:8000/callback/'

def index(request):
    return render(request, 'index.html')


def login(request):
    # Spotify authorization URL
    auth_url = 'https://accounts.spotify.com/authorize'
    scope = 'user-read-private user-read-email user-top-read'  # Required scopes
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

    # Store the access token in the session (or a better storage)
    request.session['access_token'] = token_info.get('access_token')
    return redirect(reverse('wrapper'))  # Redirect to the wrapper page


def wrapper(request):
    # Assuming you have a way to get the access token for the user
    token = request.session.get('access_token')
    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Fetch top tracks
    top_tracks_response = requests.get('https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=5', headers=headers)
    top_tracks = top_tracks_response.json().get('items', [])

    # Fetch top artists
    top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=5', headers=headers)
    top_artists = top_artists_response.json().get('items', [])

    return render(request, 'wrapper.html', {
        'top_tracks': top_tracks,
        'top_artists': top_artists
    })


def get_top_tracks(request):
    access_token = request.session.get('access_token')  # Get the access token from the session
    if not access_token:
        return redirect('login')  # Redirect to login if no access token

    # Make a request to get the user's most played tracks of this month
    response = requests.get(
        'https://api.spotify.com/v1/me/top/tracks?time_range=short_term&limit=10',  # Change the time_range if necessary
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    if response.status_code == 200:
        top_tracks_data = response.json()  # Parse the JSON response
        top_tracks = top_tracks_data.get('items', [])  # Ensure we're getting 'items' safely
    else:
        top_tracks = []  # If there's an error, return an empty list

    return render(request, 'wrapper.html', {'top_tracks': top_tracks})  # Pass the top tracks to the template


#@login_required
def logout(request):
    # Clear the user's session
    request.session.flush()
    # Redirect to a logout confirmation page
    return render(request, 'index.html')
