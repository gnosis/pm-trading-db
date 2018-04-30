#!/bin/sh

set -euo pipefail

# DEBUG set in .env
if [ ${DEBUG:-False} = True ]; then
    log_level="debug"
else
    log_level="info"
fi

echo "==> Running Celery worker <=="
exec celery worker -A gnosisdb.taskapp -Q default --hostname default@%h --loglevel $log_level -c 2 --pidfile=/tmp/celery_worker.pid
