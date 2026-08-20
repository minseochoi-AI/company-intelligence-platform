FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY sql ./sql
COPY config ./config
RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 app \
    && mkdir -p /app/data /app/artifacts \
    && chown -R app:app /app

USER app
VOLUME ["/app/data", "/app/artifacts"]
EXPOSE 8000
ENTRYPOINT ["company-intel"]
CMD ["serve"]

