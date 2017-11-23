#!/bin/sh

database_status="$(pg_isready -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME)"

case "$database_status" in
  *$ok_response*) >&2 echo "Database available" ;;
  *       )  >&2 echo "GnosisDB database is unavailable - check database status" && exit 1;;
esac


if [ -f "$HOME/var/run/celery/celerybeat.pid" ]; then
    echo "==> Removing celerybeat.pid..."
	rm "$HOME/var/run/celery/celerybeat.pid"
	echo "==> celerybeat.pid removed"
fi

# wait for RabbitMQ server and Postgres to start
echo "==> call run_celery.sh <=="

cd $PWD/gnosisdb
python manage.py createcachetable --noinput
python manage.py migrate --noinput

echo "==> run worker <=="
celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel debug --workdir="$PWD" -c 1 &
sleep 10
echo "==> run beat <=="
celery -A gnosisdb.apps beat -S django_celery_beat.schedulers:DatabaseScheduler --loglevel debug --workdir="$PWD" --pidfile=$HOME/celerybeat.pid
echo "==> run_celery.sh done <=="
