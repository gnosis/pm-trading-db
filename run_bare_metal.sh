#!/bin/bash

set -euo pipefail

source "${BASH_SOURCE%/*}/.env_bare_metal"

if [ ${DEBUG:-0} = 1 ]; then
    log_level="debug"
else
    log_level="info"
fi

python manage.py migrate

echo "==> Running Celery worker <=="
celery worker -A tradingdb.taskapp --loglevel $log_level -c 2 &

echo "==> Running Celery beat <=="
celery beat -A tradingdb.taskapp -S django_celery_beat.schedulers:DatabaseScheduler --loglevel $log_level &

# echo "==> Running Gunicorn ... "
# gunicorn --pythonpath "$PWD" config.wsgi:application --log-file=- --error-logfile=- --access-logfile '-' --log-level info -b 0.0.0.0:8000 --worker-class gevent

echo "==> Running Django Web Server..."
python manage.py runserver localhost:8000
