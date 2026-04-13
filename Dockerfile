# 1. Utilisation de Python 3.12 pour correspondre à ton pyproject.toml
FROM python:3.12-slim

# 2. Variables d'environnement pour Python et Poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="/opt/poetry/bin:$PATH"

# 3. Dépendances système (Ajout de libgl1 et nettoyage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Installation de Poetry version 2.x
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# 5. Installation des dépendances (Séparé du code pour le cache)
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-ansi

# 6. Copie du reste du projet
COPY . .

# 7. Lancement de l'API (FastAPI par défaut)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]