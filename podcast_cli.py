import os
import argparse
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 🔐 Auth Spotify
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)
console = Console()


# 🎯 Filtres personnalisés
def filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude, lang_filter):
    filtered = []
    for show in shows:
        title = show['name'].lower()
        description = show['description'].lower()
        languages = [lang.lower() for lang in show.get("languages", [])]

        if title_include and not any(kw in title for kw in title_include):
            continue
        if title_exclude and any(kw in title for kw in title_exclude):
            continue
        if desc_include and not any(kw in description for kw in desc_include):
            continue
        if desc_exclude and any(kw in description for kw in desc_exclude):
            continue
        if lang_filter and not any(lang in languages for lang in lang_filter):
            continue

        filtered.append(show)
    return filtered


# 🔎 Recherche avec pagination
def search_podcast(query, title_include, title_exclude, desc_include, desc_exclude, lang_filter, pages=1):
    all_shows = []
    query = query if query.strip() else "a"

    for page in range(pages):
        offset = page * 50
        try:
            results = sp.search(q=query, type='show', limit=50, offset=offset)
            shows = results['shows']['items']
            if not shows:
                break
            all_shows.extend(shows)
        except Exception as e:
            console.print(f"[red]Erreur lors de la pagination : {e}[/red]")
            break

    filtered_shows = filter_shows(all_shows, title_include, title_exclude, desc_include, desc_exclude, lang_filter)

    if not filtered_shows:
        console.print("[yellow]Aucun podcast ne correspond aux filtres.[/yellow]")

    return filtered_shows


# 📻 Affichage des podcasts + épisodes
def display_podcast_and_episodes(shows, max_episodes=5):
    for show in shows:
        # 🎙️ Affichage du podcast
        description = show['description'][:200] + "..."
        panel = Panel.fit(
            f"[bold yellow]{show['name']}[/bold yellow]\n"
            f"[green]Publisher:[/green] {show['publisher']}\n"
            f"[cyan]Langues:[/cyan] {', '.join(show.get('languages', []))}\n"
            f"[cyan]Episodes:[/cyan] {show['total_episodes']}\n\n"
            f"{description}\n\n"
            f"[blue]{show['external_urls']['spotify']}[/blue]",
            title="🎙️ Podcast",
            border_style="magenta"
        )
        console.print(panel)

        if max_episodes > 0:
            # 📻 Affichage des épisodes
            console.rule(f"📻 Episodes de : {show['name']}")
            try:
                episodes = sp.show_episodes(show['id'], limit=max_episodes)
                table = Table(show_header=True, header_style="bold cyan")
                table.add_column("Titre", style="bold", width=60)
                table.add_column("Date", style="dim")

                for ep in episodes['items']:
                    if not ep or 'name' not in ep or 'release_date' not in ep:
                        console.print("[red]⚠️ Épisode invalide ou corrompu, ignoré.[/red]")
                        continue
                    table.add_row(ep['name'], ep['release_date'])

                console.print(table)
            except Exception as e:
                console.print(f"[red]Erreur lors de la récupération des épisodes : {e}[/red]")


# 🚀 CLI principale
def main():
    parser = argparse.ArgumentParser(description="🎧 Spotify Podcast Explorer CLI")
    parser.add_argument("--search", help="Mot-clé global (optionnel)")
    parser.add_argument("--title-include", nargs='*', help="Mots-clés obligatoires dans le titre")
    parser.add_argument("--title-exclude", nargs='*', help="Mots-clés interdits dans le titre")
    parser.add_argument("--desc-include", nargs='*', help="Mots-clés obligatoires dans la description")
    parser.add_argument("--desc-exclude", nargs='*', help="Mots-clés interdits dans la description")
    parser.add_argument("--lang", nargs='*', help="Langue(s) ISO des podcasts (ex: fr, en)")
    parser.add_argument("--episodes", action="store_true", help="Afficher les épisodes des podcasts")
    parser.add_argument("--max-episodes", type=int, default=5, help="Nombre max d'épisodes à afficher")
    parser.add_argument("--pages", type=int, default=1, help="Nombre de pages à explorer (50 résultats max par page)")

    args = parser.parse_args()

    query = args.search if args.search else ""

    title_include = [kw.lower() for kw in args.title_include] if args.title_include else []
    title_exclude = [kw.lower() for kw in args.title_exclude] if args.title_exclude else []
    desc_include = [kw.lower() for kw in args.desc_include] if args.desc_include else []
    desc_exclude = [kw.lower() for kw in args.desc_exclude] if args.desc_exclude else []
    lang_filter = [lang.lower() for lang in args.lang] if args.lang else []

    shows = search_podcast(
        query=query,
        title_include=title_include,
        title_exclude=title_exclude,
        desc_include=desc_include,
        desc_exclude=desc_exclude,
        lang_filter=lang_filter,
        pages=args.pages
    )

    if shows:
        display_podcast_and_episodes(shows, max_episodes=args.max_episodes if args.episodes else 0)


if __name__ == "__main__":
    main()
