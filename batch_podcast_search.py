import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# --- CONFIGURATION ---

search_terms = [
    "how",
    "what",
    "why",
    "where",
    "when",
    "who",
    "can",
    "should",
    "would",
    "is",
    "are",
    "do",
    "does",
    "did",
    "have",
    "will",
    "could",
    "ever",
    "guess",
    "want",
    "ready",
    "dare",
    "stop",
    "secret",
    "happen"
]

filters = {
    "title_include": [],
    "title_exclude": [],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["en"],
    "explicit": True,
    "min_episodes": 4,
    "max_episodes": 6,
    "only_questions": True,
    "last_episode_after": "2025-03-30",
    "last_episode_before": "2025-04-01",
    "market": "FR",
    "episodes_to_show": 3
}

# --- INIT ---

load_dotenv()
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    )
)

console = Console()
raw_results = []
filtered_results = []

# --- OUTILS ---

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def get_last_episode_date(episodes):
    dates = [ep.get("release_date") for ep in episodes if ep.get("release_date")]
    if not dates:
        return None
    return max(dates)

def match_filters(show, filters, episodes, last_episode_date):
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
    if filters.get("only_questions") and not title.strip().endswith("?"):
        return False

    if filters.get("last_episode_after"):
        min_date = parse_date(filters["last_episode_after"])
        if not last_episode_date or parse_date(last_episode_date) < min_date:
            return False
    if filters.get("last_episode_before"):
        max_date = parse_date(filters["last_episode_before"])
        if not last_episode_date or parse_date(last_episode_date) > max_date:
            return False

    return True

def fetch_episodes(show_id, max_episodes):
    try:
        results = sp.show_episodes(show_id, limit=max_episodes)
        episodes = results.get("items", [])
        return [ep for ep in episodes if ep.get("name") and ep.get("release_date")]
    except Exception as e:
        console.log(f"[red]Erreur pour les épisodes de {show_id} : {e}[/red]")
        return []

def show_podcast(show, episodes):
    last_date = get_last_episode_date(episodes)
    description = show['description'][:200] + "..."
    panel = Panel.fit(
        f"[bold yellow]{show['name']}[/bold yellow]\n"
        f"[green]Publisher:[/green] {show['publisher']}\n"
        f"[cyan]Langues:[/cyan] {', '.join(show.get('languages', []))}\n"
        f"[cyan]Episodes:[/cyan] {show['total_episodes']} | Explicite: {show['explicit']}\n"
        f"[cyan]Dernier épisode :[/cyan] {last_date or 'N/A'}\n\n"
        f"{description}\n\n"
        f"[blue]{show['external_urls']['spotify']}[/blue]",
        title="🎙️ Podcast",
        border_style="magenta"
    )
    console.print(panel)

# --- TRAITEMENT ---

seen_ids = set()

for term in search_terms:
    console.rule(f"[bold green]🔍 Recherche : {term}[/bold green]")

    for offset in range(0, 1000, 50):
        try:
            results = sp.search(q=term, type='show', limit=50, offset=offset, market=filters["market"])
            shows = results.get('shows', {}).get('items', [])
            if not shows:
                break

            raw_results.extend(shows)

            for show in shows:
                if show['id'] in seen_ids:
                    continue

                episodes = fetch_episodes(show['id'], filters["episodes_to_show"])
                last_date = get_last_episode_date(episodes)

                if match_filters(show, filters, episodes, last_date):
                    show_podcast(show, episodes)
                    filtered_results.append({
                        "show": show,
                        "episodes": episodes
                    })
                    seen_ids.add(show['id'])

                time.sleep(0.2)  # Évite le throttling

        except Exception as e:
            console.print(f"[red]Erreur à l’offset {offset} pour '{term}' : {e}[/red]")
            break

# --- EXPORT FINAL ---

with open("raw_results.json", "w", encoding="utf-8") as f:
    json.dump(raw_results, f, ensure_ascii=False, indent=2)

with open("filtered_results.json", "w", encoding="utf-8") as f:
    json.dump(filtered_results, f, ensure_ascii=False, indent=2)

console.rule(f"[bold blue]✅ Total podcasts filtrés : {len(filtered_results)}[/bold blue]")
console.print("[green]Résultats exportés dans :[/green]")
console.print(" - [blue]raw_results.json[/blue]")
console.print(" - [blue]filtered_results.json[/blue]")
