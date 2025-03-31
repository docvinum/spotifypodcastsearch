# 🎧 Spotify Podcast CLI

Une application en ligne de commande pour explorer les podcasts Spotify à partir de mots-clés, avec filtres avancés et affichage enrichi grâce à `rich`.

---

## 🚀 Fonctionnalités

- Recherche de podcasts par mot-clé
- Filtres positifs (inclusion) et négatifs (exclusion) sur le titre ou la description
- Affichage des résultats enrichi avec `rich`
- Affichage des derniers épisodes pour chaque podcast trouvé
- Utilisation de l’API officielle Spotify

---

## 📦 Installation

1. Clone ce dépôt :

```bash
git clone https://github.com/votre-utilisateur/spotifypodcastsearch.git
cd spotifypodcastsearch
```

2. Crée un environnement virtuel et active-le :

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installe les dépendances :

```bash
pip install -r requirements.txt
```

4. Crée un fichier `.env` à la racine avec tes identifiants Spotify :

```env
SPOTIFY_CLIENT_ID=ton_client_id
SPOTIFY_CLIENT_SECRET=ton_client_secret
```

---

## 🧠 Utilisation

```bash
python podcast_cli.py "mot clé principal" [OPTIONS]
```

### ⚙️ Options disponibles

| Option               | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `--include`          | Liste de mots-clés obligatoires dans le titre ou la description             |
| `--exclude`          | Liste de mots-clés interdits dans le titre ou la description                |
| `--episodes`         | Affiche les épisodes de chaque podcast trouvé                               |
| `--limit`            | Nombre de résultats à explorer (par défaut : 10)                            |
| `--max-episodes`     | Nombre max d’épisodes à afficher par podcast (par défaut : 5)               |

---

## 🧪 Exemples

### Recherche simple :

```bash
python podcast_cli.py vin
```

### Recherche avec filtres positifs :

```bash
python podcast_cli.py vin --include bourgogne terroir
```

### Recherche avec filtres négatifs :

```bash
python podcast_cli.py vin --exclude whisky bière
```

### Recherche complète avec affichage des épisodes :

```bash
python podcast_cli.py vin --include bordeaux --exclude whisky --episodes
```