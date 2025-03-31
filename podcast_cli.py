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


def filter_shows(shows, include_keywords, exclude_keywords):
    filtered = []
    for show in shows:
        text = (show['name'] + " " + show['description']).lower()

        # Inclusion : au moins un mot-clé doit apparaître
        if include_keywords and not any(kw in text for kw in include_keywords):
            continue

        # Exclusion : aucun mot-clé ne doit apparaître
        if exclude_keywords and any(kw in text for kw in exclude_keywords):
            continue

        filtered.append(show)

    return filtered


def search_podcast(query, include=None, exclude=None, limit=10):
    results = sp.search(q=query, type='show', limit=limit)
    shows = results['shows']['items']
    if not shows:
        console.print("[red]Aucun résultat trouvé.[/red]")
        return []

    filtered_shows = filter_shows(shows, include, exclude)

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
    parser.add_argument("search", help="Mot-clé de recherche principal (ex: 'vin')")
    parser.add_argument("--include", nargs='*', help="Mots-clés obligatoires dans le titre ou la description")
    parser.add_argument("--exclude", nargs='*', help="Mots-clés interdits dans le titre ou la description")
    parser.add_argument("--episodes", action="store_true", help="Afficher les épisodes pour chaque podcast")
    parser.add_argument("--limit", type=int, default=10, help="Nombre maximum de résultats à explorer")
    parser.add_argument("--max-episodes", type=int, default=5, help="Nombre maximum d'épisodes à afficher")

    args = parser.parse_args()

    include_keywords = [kw.lower() for kw in args.include] if args.include else []
    exclude_keywords = [kw.lower() for kw in args.exclude] if args.exclude else []

    shows = search_podcast(args.search, include=include_keywords, exclude=exclude_keywords, limit=args.limit)

    if args.episodes and shows:
        list_episodes_for_shows(shows, max_episodes=args.max_episodes)


if __name__ == "__main__":
    main()
