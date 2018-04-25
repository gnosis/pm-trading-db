#!/bin/sh

database_status="$(pg_isready -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME)"

# wait for RabbitMQ server and Postgres to start
case "$database_status" in
  *$ok_response*) >&2 echo "Database available" ;;
  *       )  >&2 echo "GnosisDB database is unavailable - check database status" && exit 1;;
esac

echo "==> run_celery_worker.sh <=="

python manage.py migrate --noinput

echo "==> Running Celery worker <=="

# DEBUG set in .env
if [ "$DEBUG" = True ]; then
    log_level="debug"
else
    log_level="info"
fi

exec celery worker -A gnosisdb.taskapp -Q default --hostname default@%h --loglevel $log_level -c 2 --pidfile=/tmp/celery_worker.pid
