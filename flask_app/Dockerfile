# Choix de l'image de base
FROM python:3.13-slim-bookworm
ENV PYTHONUNBUFFERED 1

# Définit le répertoire de travail dans le conteneur.
WORKDIR /app

# Copie uniquement le fichier de dépendances pour profiter du cache Docker si le code change.
# Copie uniquement le fichier de dépendances pour profiter du cache Docker si le code change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

# Copie tout le dossier de l'application Flask
COPY . /app/flask_app
# COPY migrate.py /app/migrate.py

# Indique à Docker que le conteneur écoutera sur le port 5000.
EXPOSE 5000

# Lance l'application en utilisant Gunicorn.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "flask_app.app:create_app"]