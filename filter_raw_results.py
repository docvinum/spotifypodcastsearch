import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- CONFIGURATION DES FILTRES ---
filters = {
    "title_include": [],
    "title_exclude": [],
    "desc_include": [],
    "desc_exclude": [],
    "lang": ["en"],
    "explicit": True,  # True / False / None
    "min_episodes": 5,
    "max_episodes": 20,
    "market": "FR",
    "episodes_to_show": 3,
    "only_questions": True  # ou False si désactivé
}

# --- FONCTION DE FILTRAGE ---

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
    if filters.get("only_questions") and not title.strip().endswith("?"):
        return False

    return True

# --- AFFICHAGE ---

def show_podcast(podcast):
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

# --- TRAITEMENT ---

console = Console()

try:
    with open("raw_results.json", "r", encoding="utf-8") as f:
        raw_results = json.load(f)
except FileNotFoundError:
    console.print("[red]Fichier 'raw_results.json' introuvable.[/red]")
    exit(1)

filtered = [show for show in raw_results if match_filters(show, filters)]

console.rule(f"[bold green]🎯 {len(filtered)} podcasts filtrés sur {len(raw_results)} résultats[/bold green]")

for show in filtered:
    show_podcast(show)

# --- EXPORT JSON ---

with open("filtered_from_raw.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

console.print(f"[blue]Résultats filtrés exportés dans : filtered_from_raw.json[/blue]")
