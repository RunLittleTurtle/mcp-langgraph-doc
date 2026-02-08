FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    MCPDOC_TRANSPORT=streamable-http \
    LOG_LEVEL=info

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY mcpdoc /app/mcpdoc
COPY koyeb_app.py /app/koyeb_app.py

RUN pip install --upgrade pip && pip install .

EXPOSE 8000

CMD ["python", "koyeb_app.py"]
