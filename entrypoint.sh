#!/bin/bash
set -e

echo "🚀 Starting Legal Consultation Backend..."

# Wait a moment for any dependencies
sleep 2

echo "📦 Running database migrations..."
python manage.py migrate --noinput

echo "👤 Checking for superuser..."
# Create superuser if it doesn't exist (optional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

echo "✅ Setup complete! Starting Gunicorn..."

# Start Gunicorn
exec gunicorn settings.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info