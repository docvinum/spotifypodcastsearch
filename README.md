```markdown
# 🎧 Spotify Podcast CLI

Une application en ligne de commande pour explorer les podcasts Spotify selon des critères avancés : mots-clés, langues, titres, descriptions et épisodes. Le tout avec un affichage enrichi grâce à `rich`.

---

## 🚀 Fonctionnalités

- Recherche de podcasts à partir d’un mot-clé principal (optionnel)
- Filtres positifs et négatifs sur :
  - le titre
  - la description
  - la langue (codes ISO 639-1 : `fr`, `en`, `es`, etc.)
- Affichage enrichi des podcasts avec `rich`
- Affichage des épisodes récents pour chaque podcast
- Fonctionne sans interaction utilisateur (parfait pour l'automatisation)

---

## 📦 Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/votre-utilisateur/spotifypodcastsearch.git
cd spotifypodcastsearch
```

2. Créer un environnement virtuel et l’activer :

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` contenant vos identifiants API Spotify :

```env
SPOTIFY_CLIENT_ID=ton_client_id
SPOTIFY_CLIENT_SECRET=ton_client_secret
```

---

## 🧠 Utilisation

```bash
python podcast_cli.py [OPTIONS]
```

### 🔧 Options disponibles

| Option                  | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| `--search`              | Mot-clé global de recherche (optionnel)                                     |
| `--title-include`       | Mots-clés obligatoires dans le titre                                        |
| `--title-exclude`       | Mots-clés interdits dans le titre                                           |
| `--desc-include`        | Mots-clés obligatoires dans la description                                  |
| `--desc-exclude`        | Mots-clés interdits dans la description                                     |
| `--lang`                | Langues du podcast (ex : `fr`, `en`)                                        |
| `--episodes`            | Affiche les épisodes pour chaque podcast trouvé                             |
| `--limit`               | Nombre de résultats à explorer (par défaut : 10)                            |
| `--max-episodes`        | Nombre d’épisodes à afficher par podcast (par défaut : 5)                   |

---

## 🧪 Exemples

### Recherche simple sans filtre :

```bash
python podcast_cli.py --search vin
```

### Recherche avec inclusion dans le titre :

```bash
python podcast_cli.py --title-include bourgogne terroir
```

### Recherche avec exclusion dans la description :

```bash
python podcast_cli.py --desc-exclude spiritueux marketing
```

### Recherche par langue :

```bash
python podcast_cli.py --search vin --lang fr
```

### Recherche combinée avec affichage des épisodes :

```bash
python podcast_cli.py \
  --title-include bordeaux \
  --title-exclude whisky \
  --desc-include terroir \
  --desc-exclude industrie \
  --lang fr \
  --episodes
```
