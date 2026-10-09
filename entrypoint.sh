#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input

python manage.py shell << EOF
import os
from django.contrib.auth import get_user_model
User = get_user_model()
password = os.environ.get("SUPERUSERS_PASSWORD", "admin123")
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "admin@example.com", password)
EOF

GUNICORN_PORT=${PORT:-8000}
exec gunicorn config.wsgi:application --bind 0.0.0.0:$GUNICORN_PORT
