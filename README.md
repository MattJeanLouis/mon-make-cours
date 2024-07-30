# Générateur de Cours Automatique

Ce projet est un générateur de cours automatique qui utilise l'IA pour créer des cours sur des thèmes spécifiés par l'utilisateur. Il comprend une interface web Streamlit pour l'interaction utilisateur et une API FastAPI pour le traitement en arrière-plan.

## Fonctionnalités

- Génération automatique de cours basés sur un thème donné
- Interface utilisateur web intuitive avec Streamlit
- API RESTful avec FastAPI pour le traitement en arrière-plan
- Stockage des cours générés dans une base de données SQLite
- Possibilité de visualiser et de télécharger les cours générés

## Prérequis

- Python 3.9 ou supérieur
- Docker (optionnel)

## Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/MattJeanLouis/mon-make-cours.git
cd mon-make-cours
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement :
   Créez un fichier `.env` à la racine du projet et ajoutez :
```bash
OPENAI_API_KEY=your-api-key
DB_PATH=cours.db
```
## Utilisation

### Lancement local

1. Démarrez l'API FastAPI :
```bash
uvicorn app.api:app --reload
```

2. Dans un autre terminal, lancez l'interface Streamlit :
```bash
streamlit run app/streamlit_app.py
```

3. Ouvrez votre navigateur et accédez à `http://localhost:8501`

### Utilisation avec Docker

1. Construisez l'image Docker :
```bash
docker build -t mon-make-cours .
```

2. Lancez le conteneur :
```bash
docker run -p 8000:8000 -p 8501:8501 mon-make-cours
```

3. Accédez à l'interface web via `http://localhost:8501`

## Structure du projet

- `app/`: Contient le code principal de l'application
  - `api.py`: Définition de l'API FastAPI
  - `database.py`: Gestion de la base de données
  - `main.py`: Logique principale de génération de cours
  - `streamlit_app.py`: Interface utilisateur Streamlit
- `Dockerfile`: Configuration pour la conteneurisation
- `requirements.txt`: Liste des dépendances Python

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.
