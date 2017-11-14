#!/bin/sh

ok_response='accepting connections'
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

echo "==> run Celery Scheduler <=="
celery -A gnosisdb.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel debug --workdir="$PWD" --pidfile="$HOME/var/run/celery/celerybeat.pid"
