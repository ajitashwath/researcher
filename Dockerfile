FROM python:3.11-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "1", "--threads", "2", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "api:app"]