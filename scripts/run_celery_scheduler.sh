#!/bin/sh

database_status="$(pg_isready -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME)"

# wait for RabbitMQ server and Postgres to start
case "$database_status" in
  *$ok_response*) >&2 echo "Database available" ;;
  *       )  >&2 echo "GnosisDB database is unavailable - check database status" && exit 1;;
esac

echo "==> run_celery_scheduler.sh <=="

python manage.py migrate --noinput

echo "==> Running Celery beat <=="

# DEBUG set in .env
if [ "$DEBUG" = True ]; then
    log_level="debug"
else
    log_level="info"
fi

exec celery beat -A gnosisdb.taskapp -S django_celery_beat.schedulers:DatabaseScheduler --loglevel $log_level --pidfile=/tmp/celery_beat.pid
