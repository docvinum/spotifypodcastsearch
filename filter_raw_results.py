import json
import time
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.panel import Panel

# --- CONFIGURATION DES FILTRES ---

filters = {
    "title_include": [],
    "title_exclude": ["wine"],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["fr", "en"],
    "explicit": True,
    "min_episodes": 4,
    "max_episodes": 6,
    "only_questions": True,
    "last_episode_after": "2025-03-30",   # YYYY-MM-DD
    "last_episode_before": "2025-04-01"
}

# --- INITIALISATION API & CONSOLE ---

load_dotenv()
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials()
)
console = Console()

# --- OUTILS ---

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def get_last_episode_date(show_id):
    try:
        episodes = sp.show_episodes(show_id, limit=50)['items']
        dates = [ep.get("release_date") for ep in episodes if ep.get("release_date")]
        if not dates:
            return None
        return max(dates)
    except Exception as e:
        console.log(f"[red]Erreur récupération épisodes pour {show_id} : {e}[/red]")
        return None

# --- FILTRAGE ---

def match_filters(show, filters, last_episode_date=None):
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

    # Appliquer le filtre sur la date du dernier épisode
    if filters.get("last_episode_after"):
        min_date = parse_date(filters["last_episode_after"])
        if not last_episode_date or parse_date(last_episode_date) < min_date:
            return False
    if filters.get("last_episode_before"):
        max_date = parse_date(filters["last_episode_before"])
        if not last_episode_date or parse_date(last_episode_date) > max_date:
            return False

    return True

# --- AFFICHAGE ---

def show_podcast(show, last_date=None):
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

try:
    with open("raw_results.json", "r", encoding="utf-8") as f:
        raw_results = json.load(f)
except FileNotFoundError:
    console.print("[bold red]Fichier 'raw_results.json' introuvable.[/bold red]")
    exit(1)

filtered = []
console.print(f"🔍 Chargement de {len(raw_results)} podcasts depuis raw_results.json...")

for i, show in enumerate(raw_results, 1):
    show_id = show['id']
    console.log(f"({i}/{len(raw_results)}) Vérification : {show['name']}")
    last_date = get_last_episode_date(show_id)
    if match_filters(show, filters, last_episode_date=last_date):
        show_podcast(show, last_date)
        show["last_episode_date"] = last_date
        filtered.append(show)
    time.sleep(0.2)  # pour éviter les erreurs d’API

# --- EXPORT FINAL ---

with open("filtered_from_raw.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

console.rule(f"[bold green]🎯 {len(filtered)} podcasts filtrés sur {len(raw_results)}[/bold green]")
console.print("[green]Résultats exportés dans :[/green] [blue]filtered_from_raw.json[/blue]")
