### podcast_cli.py ###
# Rechercher les podcasts contenant "vin", incluant "bourgogne" ou "terroir", mais excluant "whisky"
# python podcast_cli.py vin --include bourgogne terroir --exclude whisky --episodes

import os
import argparse
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Load .env credentials
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)
console = Console()


def filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude):
    filtered = []
    for show in shows:
        title = show['name'].lower()
        description = show['description'].lower()

        # Filtres sur le titre
        if title_include and not any(kw in title for kw in title_include):
            continue
        if title_exclude and any(kw in title for kw in title_exclude):
            continue

        # Filtres sur la description
        if desc_include and not any(kw in description for kw in desc_include):
            continue
        if desc_exclude and any(kw in description for kw in desc_exclude):
            continue

        filtered.append(show)
    return filtered


def search_podcast(query, title_include, title_exclude, desc_include, desc_exclude, limit=10):
    results = sp.search(q=query, type='show', limit=limit)
    shows = results['shows']['items']
    if not shows:
        console.print("[red]Aucun résultat trouvé.[/red]")
        return []

    filtered_shows = filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude)

    if not filtered_shows:
        console.print("[yellow]Aucun podcast ne correspond aux filtres.[/yellow]")
        return []

    for i, show in enumerate(filtered_shows, 1):
        description = show['description'][:200] + "..."
        panel = Panel.fit(
            f"[bold yellow]{show['name']}[/bold yellow]\n"
            f"[green]Publisher:[/green] {show['publisher']}\n"
            f"[cyan]Episodes:[/cyan] {show['total_episodes']}\n\n"
            f"{description}\n\n"
            f"[blue]{show['external_urls']['spotify']}[/blue]",
            title=f"🎙️ Podcast {i}",
            border_style="magenta"
        )
        console.print(panel)

    return filtered_shows

def list_episodes_for_shows(shows, max_episodes=5):
    for show in shows:
        console.rule(f"📻 Episodes de : {show['name']}")
        episodes = sp.show_episodes(show['id'], limit=max_episodes)
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Titre", style="bold", width=60)
        table.add_column("Date", style="dim")

        for ep in episodes['items']:
            table.add_row(ep['name'], ep['release_date'])

        console.print(table)

def main():
    parser = argparse.ArgumentParser(description="🎧 Spotify Podcast Explorer CLI")
    parser.add_argument("search", help="Mot-clé principal pour la recherche globale (dans Spotify)")
    
    # Nouveaux arguments : filtres par champ
    parser.add_argument("--title-include", nargs='*', help="Mots-clés à inclure dans le titre")
    parser.add_argument("--title-exclude", nargs='*', help="Mots-clés à exclure du titre")
    parser.add_argument("--desc-include", nargs='*', help="Mots-clés à inclure dans la description")
    parser.add_argument("--desc-exclude", nargs='*', help="Mots-clés à exclure de la description")
    
    # Options existantes
    parser.add_argument("--episodes", action="store_true", help="Afficher les épisodes pour chaque podcast")
    parser.add_argument("--limit", type=int, default=10, help="Nombre maximum de résultats à explorer")
    parser.add_argument("--max-episodes", type=int, default=5, help="Nombre maximum d'épisodes à afficher")

    args = parser.parse_args()

    # Nettoyage des mots-clés (lowercase)
    title_include = [kw.lower() for kw in args.title_include] if args.title_include else []
    title_exclude = [kw.lower() for kw in args.title_exclude] if args.title_exclude else []
    desc_include = [kw.lower() for kw in args.desc_include] if args.desc_include else []
    desc_exclude = [kw.lower() for kw in args.desc_exclude] if args.desc_exclude else []

    # Recherche et affichage des podcasts
    shows = search_podcast(
        query=args.search,
        title_include=title_include,
        title_exclude=title_exclude,
        desc_include=desc_include,
        desc_exclude=desc_exclude,
        limit=args.limit
    )

    # Affichage des épisodes si demandé
    if args.episodes and shows:
        list_episodes_for_shows(shows, max_episodes=args.max_episodes)

if __name__ == "__main__":
    main()
