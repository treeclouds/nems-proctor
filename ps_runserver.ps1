# Set environment variables
$env:DATABASE_URL = "postgresql://nems-proctor:P@ssw0rd123@127.0.0.1:5432/nems-proctor-db"
$env:CELERY_BROKER_URL = "redis://redis:6379"
$env:USE_DOCKER = "no"
$env:DJANGO_SETTINGS_MODULE="config.settings.local"
