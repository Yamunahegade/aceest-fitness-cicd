FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ACEEST_DB=/data/aceest_fitness.db
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app.py pytest.ini ./
COPY tests ./tests
ARG APP_VERSION=1.1.0
ENV APP_VERSION=${APP_VERSION}
RUN useradd --no-create-home --shell /usr/sbin/nologin appuser \
    && mkdir /data && chown appuser /data
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request as u; u.urlopen('http://localhost:5000/health')" || exit 1
# one worker: SQLite is a single-writer database
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "app:app"]
