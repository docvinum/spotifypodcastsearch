import os
import argparse
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)
console = Console()


def format_query(search_terms):
    if not search_terms:
        return "a"
    return " AND ".join([f'"{term}"' if " " in term else term for term in search_terms])


def filter_shows(shows, title_include, title_exclude, desc_include, desc_exclude, lang_filter,
                 min_episodes, max_episodes, explicit=None, debug=False):
    filtered = []
    for show in shows:
        reasons = []
        title = show['name'].lower()
        description = show['description'].lower()
        languages = [lang.lower() for lang in show.get("languages", [])]
        total_eps = show.get('total_episodes', 0)
        is_explicit = show.get("explicit")

        if title_include and not any(kw in title for kw in title_include):
            reasons.append("🔸 titre ne contient pas les mots-clés requis")
        if title_exclude and any(kw in title for kw in title_exclude):
            reasons.append("🔸 titre contient un mot-clé exclu")
        if desc_include and not any(kw in description for kw in desc_include):
            reasons.append("🔸 description ne contient pas les mots-clés requis")
        if desc_exclude and any(kw in description for kw in desc_exclude):
            reasons.append("🔸 description contient un mot-clé exclu")
        if lang_filter and not any(lang in languages for lang in lang_filter):
            reasons.append(f"🔸 langue(s) {languages} ≠ {lang_filter}")
        if explicit is not None and is_explicit != explicit:
            reasons.append(f"🔸 explicite={is_explicit} ≠ attendu={explicit}")
        if min_episodes is not None and total_eps < min_episodes:
            reasons.append(f"🔸 {total_eps} épisode(s) < {min_episodes}")
        if max_episodes is not None and total_eps > max_episodes:
            reasons.append(f"🔸 {total_eps} épisode(s) > {max_episodes}")

        if reasons:
            if debug:
                console.print(f"[dim]❌ {show['name']} ignoré\n  " + "\n  ".join(reasons) + "\n[/dim]")
            continue

        filtered.append(show)
    return filtered


def fetch_shows(query, offset, market):
    try:
        results = sp.search(q=query, type='show', limit=50, offset=offset, market=market)
        return results['shows']['items']
    except Exception as e:
        console.print(f"[red]Erreur Spotify API : {e}[/red]")
        return []


def display_podcast_and_episodes(shows, max_episodes=5):
    for show in shows:
        description = show['description'][:200] + "..."
        panel = Panel.fit(
            f"[bold yellow]{show['name']}[/bold yellow]\n"
            f"[green]Publisher:[/green] {show['publisher']}\n"
            f"[cyan]Langues:[/cyan] {', '.join(show.get('languages', []))}\n"
            f"[cyan]Episodes:[/cyan] {show['total_episodes']}\n"
            f"[cyan]Explicite:[/cyan] {show['explicit']}\n\n"
            f"{description}\n\n"
            f"[blue]{show['external_urls']['spotify']}[/blue]",
            title="🎙️ Podcast",
            border_style="magenta"
        )
        console.print(panel)

        if max_episodes > 0:
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


def prompt_continue():
    response = input("\nSouhaitez-vous charger les 50 podcasts suivants ? (O/N) : ").strip().lower()
    return response in ["o", "oui", "y", "yes"]


def main():
    parser = argparse.ArgumentParser(
        description="🎧 Spotify Podcast Explorer CLI – Recherche avancée de podcasts",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    search_group = parser.add_mutually_exclusive_group()
    search_group.add_argument("--search", nargs='+', help="Mots-clés combinés automatiquement avec AND")
    search_group.add_argument("--raw-query", help="Requête avancée Spotify (ex: 'wine NOT whisky')")

    parser.add_argument("--market", help="Code pays ISO (ex: FR, US, DE)", default=None)
    parser.add_argument("--title-include", nargs='*', help="Mots-clés à inclure dans le titre")
    parser.add_argument("--title-exclude", nargs='*', help="Mots-clés à exclure du titre")
    parser.add_argument("--desc-include", nargs='*', help="Mots-clés à inclure dans la description")
    parser.add_argument("--desc-exclude", nargs='*', help="Mots-clés à exclure de la description")
    parser.add_argument("--lang", nargs='*', help="Langue(s) ISO (ex: fr, en)")
    parser.add_argument("--explicit", choices=["yes", "no"], help="Filtrer selon le contenu explicite")
    parser.add_argument("--min-episodes", type=int, help="Nombre minimum d'épisodes")
    parser.add_argument("--max-episodes", type=int, help="Nombre maximum d'épisodes")
    parser.add_argument("--episodes", action="store_true", help="Afficher les épisodes")
    parser.add_argument("--max-episodes-to-show", type=int, default=5, help="Nombre d'épisodes à afficher")
    parser.add_argument("--debug", action="store_true", help="Afficher les raisons de rejet")

    args = parser.parse_args()

    query = args.raw_query if args.raw_query else format_query(args.search)
    offset = 0

    title_include = [kw.lower() for kw in args.title_include] if args.title_include else []
    title_exclude = [kw.lower() for kw in args.title_exclude] if args.title_exclude else []
    desc_include = [kw.lower() for kw in args.desc_include] if args.desc_include else []
    desc_exclude = [kw.lower() for kw in args.desc_exclude] if args.desc_exclude else []
    lang_filter = [lang.lower() for lang in args.lang] if args.lang else []
    explicit_bool = True if args.explicit == "yes" else False if args.explicit == "no" else None

    while True:
        if offset + 50 > 1000:
            console.print("[red]⚠️ Limite API Spotify atteinte : 1000 résultats max.[/red]")
            break

        shows = fetch_shows(query, offset, args.market)
        if not shows:
            break

        filtered = filter_shows(
            shows,
            title_include, title_exclude,
            desc_include, desc_exclude,
            lang_filter,
            args.min_episodes, args.max_episodes,
            explicit=explicit_bool,
            debug=args.debug
        )

        if filtered:
            display_podcast_and_episodes(
                filtered,
                max_episodes=args.max_episodes_to_show if args.episodes else 0
            )
        else:
            console.print("[yellow]Aucun podcast ne correspond aux filtres sur cette page.[/yellow]")

        offset += 50
        if not prompt_continue():
            break


if __name__ == "__main__":
    main()
