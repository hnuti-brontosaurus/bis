#!/bin/sh

set -e

# Commands available using `docker-compose run backend [COMMAND]`
case "$1" in
    test)
        python -m pytest --durations=3
    ;;
    dev)
        python manage.py migrate
        PYTHONUNBUFFERED=1 python manage.py runserver ${APP_HOST}:${APP_PORT}
    ;;
    testing)
        # MIGRATION_MODULES is disabled when ENVIRONMENT=testing, so --run-syncdb
        # creates tables directly from current models against a fresh DB.
        # -v 0 suppresses the post-migrate autodetector check, which crashes in
        # --run-syncdb mode on swappable-model deps.
        python manage.py migrate --run-syncdb -v 0
        PYTHONUNBUFFERED=1 python manage.py runserver ${APP_HOST}:${APP_PORT}
    ;;
    *)
        python manage.py collectstatic --no-input
        python manage.py migrate
        python manage.py create_categories

        echo "Running Supervisorded Gunicorn..."
        gunicorn --threads 8 --env DJANGO_SETTINGS_MODULE=project.settings project.wsgi -b ${APP_HOST}:${APP_PORT} -t 1800
    ;;
esac
