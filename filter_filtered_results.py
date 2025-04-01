import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- CONFIGURATION DES FILTRES ---

filters = {
    "title_include": ["wine", "vin"],
    "title_exclude": [],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["en"],
    "explicit": True,
    "min_episodes": 5,
    "max_episodes": 20,
    "only_questions": True,
    "last_episode_after": "2025-01-01",   # YYYY-MM-DD
    "last_episode_before": "2025-03-31"
}

# --- OUTILS ---

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def get_last_episode_date(episodes):
    dates = [ep.get("release_date") for ep in episodes if ep.get("release_date")]
    if not dates:
        return None
    latest_str = max(dates)
    return parse_date(latest_str)

# --- FILTRE PRINCIPAL ---

def match_filters(entry, filters):
    show = entry["show"]
    episodes = entry.get("episodes", [])

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

    latest_date = get_last_episode_date(episodes)
    if filters.get("last_episode_after"):
        min_date = parse_date(filters["last_episode_after"])
        if not latest_date or latest_date < min_date:
            return False
    if filters.get("last_episode_before"):
        max_date = parse_date(filters["last_episode_before"])
        if not latest_date or latest_date > max_date:
            return False

    return True

# --- AFFICHAGE ---

def show_podcast(entry):
    show = entry["show"]
    episodes = entry.get("episodes", [])

    last_date = max((ep["release_date"] for ep in episodes if ep.get("release_date")), default="N/A")
    description = show['description'][:200] + "..."
    panel = Panel.fit(
        f"[bold yellow]{show['name']}[/bold yellow]\n"
        f"[green]Publisher:[/green] {show['publisher']}\n"
        f"[cyan]Langues:[/cyan] {', '.join(show.get('languages', []))}\n"
        f"[cyan]Episodes:[/cyan] {show['total_episodes']} | Explicite: {show['explicit']}\n"
        f"[cyan]Dernier épisode :[/cyan] {last_date}\n\n"
        f"{description}\n\n"
        f"[blue]{show['external_urls']['spotify']}[/blue]",
        title="🎙️ Podcast",
        border_style="magenta"
    )
    console.print(panel)

# --- TRAITEMENT ---

console = Console()

try:
    with open("filtered_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    console.print("[bold red]Fichier 'filtered_results.json' introuvable.[/bold red]")
    exit(1)

filtered = [entry for entry in data if match_filters(entry, filters)]

console.rule(f"[bold green]🎯 {len(filtered)} podcasts filtrés sur {len(data)}[/bold green]")

for entry in filtered:
    show_podcast(entry)

# --- EXPORT FINAL ---

with open("filtered_from_filtered.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

console.print("[green]Résultats exportés dans :[/green] [blue]filtered_from_filtered.json[/blue]")
