#!/bin/bash

addgroup celery
useradd -ms /bin/bash celery -g celery

database_status="$(pg_isready -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME)"

case "$database_status" in
  *$ok_response*) >&2 echo "Database available" ;;
  *       )  >&2 echo "GnosisDB database is unavailable - check database status" && exit 1;;
esac


if [ -f "$HOME/celerybeat.pid" ]; then
    echo "==> Removing celerybeat.pid..."
	rm "$HOME/celerybeat.pid"
	echo "==> celerybeat.pid removed"
fi

# wait for RabbitMQ server and Postgres to start
echo "==> call run_celery.sh <=="

python manage.py migrate --noinput

shutdown() {
    echo "Shuting down gracefully celery"
    kill -3 "$child"
}


trap shutdown SIGTERM SIGINT

echo "==> run beat <=="
celery -A gnosisdb.taskapp beat -S django_celery_beat.schedulers:DatabaseScheduler --loglevel debug --pidfile=$HOME/celerybeat.pid &

child=$!
wait $!
