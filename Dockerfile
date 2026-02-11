# Builder Stage
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y curl build-essential
RUN curl -sSl https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
COPY pyproject.toml poetry.lock /app/

#RUN poetry lock --no-interaction
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --only main --no-interaction --no-ansi
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"
COPY src /app/src
COPY src/main.py /app/main.py
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# Runtime Stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /app /app
COPY --from=builder /usr/local/bin /usr/local/bin
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"
CMD ["uvicorn", "src.main:app","--reload", "--host", "0.0.0.0", "--port", "8000"]