import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Replace with your actual keys from Spotify Developer Dashboard
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'

# Auth
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Search for a podcast show (e.g. "The Daily")
query = "The Daily"
results = sp.search(q=query, type='show', limit=3)

for show in results['shows']['items']:
    print(f"🎙️ Title: {show['name']}")
    print(f"   Publisher: {show['publisher']}")
    print(f"   Description: {show['description'][:100]}...")
    print(f"   Total Episodes: {show['total_episodes']}")
    print(f"   Link: {show['external_urls']['spotify']}")
    print("---")

# You can also fetch episodes of a specific show
show_id = results['shows']['items'][0]['id']
episodes = sp.show_episodes(show_id, limit=5)

print("\n📻 Latest Episodes:")
for ep in episodes['items']:
    print(f"- {ep['name']} ({ep['release_date']})")

