FROM python:3.12-slim

# 1. Variables d'environnement optimisées
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    USE_TF=0 \
    USE_TORCH=1 \
    PATH="/opt/poetry/bin:$PATH"

# 2. Dépendances système (libgl1 est vital pour docTR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgl1 \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.0.1

WORKDIR /app

# 4. Installation des dépendances
COPY pyproject.toml poetry.lock* ./
# Note: Si tu as besoin de tf2onnx ou protobuf spécifique, 
# assure-toi qu'ils sont dans ton pyproject.toml
RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

# 5. Exposition du port pour FastAPI
EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]