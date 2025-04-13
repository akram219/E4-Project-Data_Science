# Image de base avec Python
FROM python:3.10-slim

# Créer le dossier de travail dans le conteneur
WORKDIR /app

# Copier les fichiers dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par Flask
EXPOSE 5000

# Lancer l'app
CMD ["python", "backend.py"]
