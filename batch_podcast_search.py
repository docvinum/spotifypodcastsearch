import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# --- CONFIGURATION ---

# 🔍 Mots-clés de recherche
search_terms = [
    "natural wine",
    "organic wine",
    "vin nature",
    "vin bio",
    "oenologie"
]

# 🎯 Filtres à appliquer
filters = {
    "title_include": ["wine", "vin"],
    "title_exclude": [],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["fr", "en"],
    "explicit": None,  # True / False / None
    "min_episodes": 5,
    "max_episodes": None,
    "market": "FR",
    "episodes_to_show": 3
}

# --- INITIALISATION ---

load_dotenv()
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)
console = Console()


# --- LOGIQUE ---

def match_filters(show, filters):
    title = show['name'].lower()
    description = show['description'].lower()
    languages = [l.lower() for l in show.get("languages", [])]
    total_eps = show.get("total_episodes", 0)
    is_explicit = show.get("explicit", None)

    if filters["title_include"] and not any(kw in title for kw in filters["title_include"]):
        return False
    if filters["title_exclude"] and any(kw in title for kw in filters["title_exclude"]):
        return False
    if filters["desc_include"] and not any(kw in description for kw in filters["desc_include"]):
        return False
    if filters["desc_exclude"] and any(kw in description for kw in filters["desc_exclude"]):
        return False
    if filters["lang"] and not any(lang in languages for lang in filters["lang"]):
        return False
    if filters["explicit"] is not None and is_explicit != filters["explicit"]:
        return False
    if filters["min_episodes"] and total_eps < filters["min_episodes"]:
        return False
    if filters["max_episodes"] and total_eps > filters["max_episodes"]:
        return False

    return True


def fetch_episodes(show_id, max_episodes):
    try:
        episodes = sp.show_episodes(show_id, limit=max_episodes)['items']
        return [ep for ep in episodes if ep and 'name' in ep and 'release_date' in ep]
    except Exception as e:
        console.print(f"[red]Erreur pour les épisodes : {e}[/red]")
        return []


def show_podcast(podcast, episodes):
    description = podcast['description'][:200] + "..."
    panel = Panel.fit(
        f"[bold yellow]{podcast['name']}[/bold yellow]\n"
        f"[green]Publisher:[/green] {podcast['publisher']}\n"
        f"[cyan]Langues:[/cyan] {', '.join(podcast.get('languages', []))}\n"
        f"[cyan]Episodes:[/cyan] {podcast['total_episodes']} | Explicite: {podcast['explicit']}\n\n"
        f"{description}\n\n"
        f"[blue]{podcast['external_urls']['spotify']}[/blue]",
        title="🎙️ Podcast",
        border_style="magenta"
    )
    console.print(panel)

    if episodes:
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Titre", style="bold", width=60)
        table.add_column("Date", style="dim")
        for ep in episodes:
            table.add_row(ep['name'], ep['release_date'])
        console.print(table)


# --- TRAITEMENT ---

seen_ids = set()

for term in search_terms:
    console.rule(f"[bold green]🔍 Recherche : {term}[/bold green]")
    try:
        results = sp.search(q=term, type='show', limit=50, market=filters["market"])
        for show in results['shows']['items']:
            if show['id'] in seen_ids:
                continue
            if match_filters(show, filters):
                episodes = fetch_episodes(show['id'], filters["episodes_to_show"])
                show_podcast(show, episodes)
                seen_ids.add(show['id'])
    except Exception as e:
        console.print(f"[red]Erreur avec la recherche '{term}' : {e}[/red]")

