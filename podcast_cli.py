import os
import argparse
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 🔐 Authentification Spotify via .env
load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# 🎨 Console Rich
console = Console()

# 🎯 Filtres personnalisés
def filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude, lang_filter):
    filtered = []
    for show in shows:
        title = show['name'].lower()
        description = show['description'].lower()
        languages = [lang.lower() for lang in show.get("languages", [])]

        # Titre
        if title_include and not any(kw in title for kw in title_include):
            continue
        if title_exclude and any(kw in title for kw in title_exclude):
            continue

        # Description
        if desc_include and not any(kw in description for kw in desc_include):
            continue
        if desc_exclude and any(kw in description for kw in desc_exclude):
            continue

        # Langue
        if lang_filter and not any(lang in languages for lang in lang_filter):
            continue

        filtered.append(show)
    return filtered

# 🔎 Recherche de podcasts
def search_podcast(query, title_include, title_exclude, desc_include, desc_exclude, lang_filter, limit=10):
    query = query if query.strip() else "a"  # Fallback pour forcer des résultats
    results = sp.search(q=query, type='show', limit=limit)
    shows = results['shows']['items']

    if not shows:
        console.print("[red]Aucun résultat trouvé.[/red]")
        return []

    filtered_shows = filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude, lang_filter)

    if not filtered_shows:
        console.print("[yellow]Aucun podcast ne correspond aux filtres.[/yellow]")
        return []

    return filtered_shows

# 📻 Affichage des épisodes
def display_podcast_and_episodes(shows, max_episodes=5):
    for show in shows:
        # 🎙️ Podcast
        description = show['description'][:200] + "..."
        panel = Panel.fit(
            f"[bold yellow]{show['name']}[/bold yellow]\n"
            f"[green]Publisher:[/green] {show['publisher']}\n"
            f"[cyan]Langues:[/cyan] {', '.join(show.get('languages', []))}\n"
            f"[cyan]Episodes:[/cyan] {show['total_episodes']}\n\n"
            f"{description}\n\n"
            f"[blue]{show['external_urls']['spotify']}[/blue]",
            title=f"🎙️ Podcast",
            border_style="magenta"
        )
        console.print(panel)

        # 📻 Épisodes
        console.rule(f"📻 Episodes de : {show['name']}")
        episodes = sp.show_episodes(show['id'], limit=max_episodes)
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Titre", style="bold", width=60)
        table.add_column("Date", style="dim")

        for ep in episodes['items']:
            table.add_row(ep['name'], ep['release_date'])

        console.print(table)

# 🚀 Point d’entrée
def main():
    parser = argparse.ArgumentParser(description="🎧 Spotify Podcast Explorer CLI")

    parser.add_argument("--search", help="Mot-clé principal pour la recherche globale (optionnel)")
    parser.add_argument("--title-include", nargs='*', help="Mots-clés à inclure dans le titre")
    parser.add_argument("--title-exclude", nargs='*', help="Mots-clés à exclure du titre")
    parser.add_argument("--desc-include", nargs='*', help="Mots-clés à inclure dans la description")
    parser.add_argument("--desc-exclude", nargs='*', help="Mots-clés à exclure de la description")
    parser.add_argument("--lang", nargs='*', help="Langue(s) ISO 639-1 des podcasts (ex: fr, en, es)")
    parser.add_argument("--episodes", action="store_true", help="Afficher les épisodes pour chaque podcast")
    parser.add_argument("--limit", type=int, default=10, help="Nombre maximum de résultats à explorer")
    parser.add_argument("--max-episodes", type=int, default=5, help="Nombre maximum d'épisodes à afficher")

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
        limit=args.limit
    )

    if args.episodes and shows:
        display_podcast_and_episodes(shows, max_episodes=args.max_episodes)
    elif shows:
        display_podcast_and_episodes(shows, max_episodes=0)  # Affiche juste les podcasts


if __name__ == "__main__":
    main()
