# --- Builder Stage ---
FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y curl build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy ONLY the dependency files first
COPY pyproject.toml poetry.lock ./

# Install dependencies globally in the builder container
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main --no-interaction --no-ansi

# Now copy the application structure
COPY src ./src
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# --- Runtime Stage ---
FROM python:3.12-slim
WORKDIR /app

# Copy libraries and binaries from builder
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
# Copy the /app folder (contains src, alembic, etc.)
COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1
# Ensure the path is set so 'uvicorn' is recognized
ENV PATH="/usr/local/bin:$PATH"

# THE FIX: We reference src.main:app because main.py is INSIDE the src folder.
# Change the path to run from the root, not the src folder
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]