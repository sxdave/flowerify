from dotenv import load_dotenv
from flask import Flask, redirect, request, jsonify, session, render_template
import requests
import os
import urllib.parse
from datetime import datetime

load_dotenv()

authorize_url = os.getenv("AUTHORIZE_URL")
token_url = os.getenv("TOKEN_URL")
redirect_uri = os.getenv("REDIRECT_URI")
api_base = os.getenv("API_BASE")
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

MY_PORT = 8000 # random.randrange(1<<12, 1<<15)

app = Flask(__name__)
app.secret_key = '53d355f8-571a-4590-a310-f9579450851'

@app.route('/')
def index():
    return render_template('index.html')
    #return "Welcome to Spotify API Application <a href = '/login'> Log in With Spotify </a>"

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def authorize():
    scope = "user-read-private user-read-email user-read-recently-played user-top-read"

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': redirect_uri,
        'show_dialog': True
    }
    auth_url = f"{authorize_url}?{urllib.parse.urlencode(params)}"
    print(auth_url)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        reponse = requests.post(token_url, data = req_body)
        token = reponse.json()

        session['access_token'] = token['access_token']
        session['refresh_token'] = token['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token['expires_in']

        return redirect('/flowerify/short_term')

@app.route('/flowerify/<time>')
def flowerify(time):
    if 'access_token' not in session:
        return redirect('/login')
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
    }
    # response = requests.get(api_base + "me/top/tracks?time_range=long_term", headers = headers)
    # artists = response.json()

    # return artists
    
    toptracks, toptracksimages = top_tracks(headers, time)
    topartists, topartistsimages = top_artists(headers, time)
    
    return render_template('main.html', tracks = toptracks, artists = topartists, track_images = toptracksimages, artist_images = topartistsimages)

def playlists(headers):
    # if 'access_token' not in session:
    #     return redirect('/login')
    # headers = {
    #     'Authorization': f"Bearer {session['access_token']}"
    # }

    response = requests.get(api_base + "me/playlists", headers = headers)
    playlists = response.json()
    playlist_names = []
    
    for item in playlists['items']:
        playlist_names.append(item['name'])
    
    return playlist_names
    #return jsonify(playlists) 

def recently_played(headers):
    # if 'access_token' not in session:
    #     return redirect('/login')
    # headers = {
    #     'Authorization': f"Bearer {session['access_token']}"
    # }

    response = requests.get(api_base + "me/player/recently-played", headers = headers)
    recently_played = response.json()
    recently_played_tracks = []

    for item in recently_played['items']:
        recently_played_tracks.append(item['name'])
    
    
    return recently_played_tracks
    #return jsonify(recently_played)

def top_artists(headers, time):
    # if 'access_token' not in session:
    #     return redirect('/login')
    # headers = {
    #     'Authorization': f"Bearer {session['access_token']}"
    # }
    
    response = requests.get(api_base + "me/top/artists?time_range=" + time, headers = headers)
    artists = response.json()
    top_artists = []
    top_artist_images = []

    for item in artists['items']:
        top_artists.append(item['name'])
        top_artist_images.append(item['images'][0]['url'])
    
    return top_artists, top_artist_images
    
    #return jsonify(artists)

def top_tracks(headers, time):
    # if 'access_token' not in session:
    #     return redirect('/login')
    # headers = {
    #     'Authorization': f"Bearer {session['access_token']}",
    # }
    
    response = requests.get(api_base + "me/top/tracks?time_range=" + time, headers = headers)
    tracks = response.json()
    top_tracks = []
    top_track_images = []

    for item in tracks['items']:
        top_tracks.append(item['name'])
        top_track_images.append(item['album']['images'][0]['url'])
    return top_tracks, top_track_images
    # return jsonify(tracks)

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = MY_PORT, debug = True)

