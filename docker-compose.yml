version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-farmdirect}
      POSTGRES_USER: ${POSTGRES_USER:-farmdirect}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-farmdirect_secret}
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-farmdirect}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: >
      sh -c "python manage.py migrate --noinput &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2"
    volumes:
      - ./backend:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: celery -A config worker -l info --concurrency=4
    volumes:
      - ./backend:/app
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./backend:/app
    env_file:
      - .env
    environment:
      - DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-config.settings.production}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost/api}
    depends_on:
      - backend

  nginx:
    image: nginx:1.25-alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - static_volume:/var/www/static
      - media_volume:/var/www/media
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
