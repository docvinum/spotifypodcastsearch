import os
import time
import json
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# --- CONFIGURATION ---

search_terms = [
    "natural wine",
    "organic wine",
    "vin nature",
    "vin bio",
    "oenologie"
]

filters = {
    "title_include": ["wine", "vin"],
    "title_exclude": [],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["fr", "en"],
    "explicit": None,
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
log_file = open("batch.log", "w", encoding="utf-8")
raw_results = []
filtered_results = []

def log(msg):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    log_file.write(f"{timestamp} {msg}\n")
    log_file.flush()
    console.log(msg)

# --- FONCTIONS ---

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
        results = sp.show_episodes(show_id, limit=max_episodes)
        episodes = results.get("items", [])
        log(f"↳ {len(episodes)} épisode(s) récupéré(s) pour {show_id}")
        return [ep for ep in episodes if ep and 'name' in ep and 'release_date' in ep]
    except Exception as e:
        log(f"Erreur récupération épisodes pour {show_id} : {e}")
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
total_found = 0

for term in search_terms:
    console.rule(f"[bold green]🔍 Recherche : {term}[/bold green]")
    log(f"Recherche : {term}")
    found_for_term = 0

    for offset in range(0, 1000, 50):
        try:
            log(f"  → Offset {offset}")
            results = sp.search(q=term, type='show', limit=50, offset=offset, market=filters["market"])
            shows = results.get('shows', {}).get('items', [])
            log(f"  → {len(shows)} shows reçus")

            if not shows:
                break

            raw_results.extend(shows)

            for show in shows:
                if show['id'] in seen_ids:
                    continue
                if match_filters(show, filters):
                    episodes = fetch_episodes(show['id'], filters["episodes_to_show"])
                    show_podcast(show, episodes)
                    filtered_results.append({
                        "show": show,
                        "episodes": episodes
                    })
                    seen_ids.add(show['id'])
                    found_for_term += 1

            time.sleep(0.2)

        except Exception as e:
            log(f"Erreur à l’offset {offset} pour '{term}' : {e}")
            break

    if found_for_term == 0:
        log(f"⚠ Aucun résultat filtré pour '{term}'")

    total_found += found_for_term

log_file.close()

# --- EXPORT FINAL ---

with open("raw_results.json", "w", encoding="utf-8") as f:
    json.dump(raw_results, f, ensure_ascii=False, indent=2)

with open("filtered_results.json", "w", encoding="utf-8") as f:
    json.dump(filtered_results, f, ensure_ascii=False, indent=2)

console.rule(f"[bold blue]✅ Total podcasts filtrés : {total_found}[/bold blue]")
console.print("[green]Les résultats ont été enregistrés dans :[/green]")
console.print(" - [blue]batch.log[/blue] (log détaillé)")
console.print(" - [blue]raw_results.json[/blue] (tous les résultats)")
console.print(" - [blue]filtered_results.json[/blue] (podcasts filtrés + épisodes)")
