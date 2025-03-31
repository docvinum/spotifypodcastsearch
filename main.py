import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Set up Spotify auth
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Search for a podcast show
query = "The Daily"
results = sp.search(q=query, type='show', limit=3)

for show in results['shows']['items']:
    print(f"🎙️ Title: {show['name']}")
    print(f"   Publisher: {show['publisher']}")
    print(f"   Description: {show['description'][:100]}...")
    print(f"   Total Episodes: {show['total_episodes']}")
    print(f"   Link: {show['external_urls']['spotify']}")
    print("---")
