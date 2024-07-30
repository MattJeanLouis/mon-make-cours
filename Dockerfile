# Utiliser une image Python officielle comme image de base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de dépendances et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application dans le conteneur
COPY . .

# Exposer les ports pour FastAPI et Streamlit
EXPOSE 8000 8501

# Créer un script pour lancer à la fois FastAPI et Streamlit
RUN echo '#!/bin/bash\n\
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload &\n\
streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Commande pour exécuter l'application
CMD ["/app/start.sh"]