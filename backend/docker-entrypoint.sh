#!/bin/sh

set -e

# Wait for Postgres
until PGPASSWORD=${DB_PASSWORD} psql -h ${DB_HOST} -U ${DB_USERNAME} -c '\q' ${DB_NAME}; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Commands available using `docker-compose run backend [COMMAND]`
case "$1" in
    python)
        echo "Run migrations and collect static files"
        python manage.py collectstatic --no-input
        python manage.py migrate

        python manage.py shell
    ;;
    test)
        python -m pytest --durations=3
    ;;
    dev)
        echo "Run migrations and collect static files"
        python manage.py collectstatic --no-input
        python manage.py migrate

        echo "Running Dev Server..."
        PYTHONUNBUFFERED=1 python manage.py runserver ${APP_HOST}:${APP_PORT}
    ;;
    manage)
        echo "Run migrations and collect static files"
        python manage.py collectstatic --no-input

        python manage.py $2
    ;;
    *)
        echo "Run migrations and collect static files"
        python manage.py collectstatic --no-input
        python manage.py migrate

        # Gunicorn
        echo "Running Supervisorded Gunicorn..."
        gunicorn --env DJANGO_SETTINGS_MODULE=project.settings project.wsgi -b ${APP_HOST}:${APP_PORT} -t 300
    ;;
esac
