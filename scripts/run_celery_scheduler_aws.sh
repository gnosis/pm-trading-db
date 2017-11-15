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

cd $PWD/gnosisdb

echo "==> run Celery Scheduler <=="
echo "==> with user: "
whoami
echo "<=="
echo "==> Executing command:"
echo "celery -A gnosisdb.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel $CELERY_LOG_LEVEL --workdir=\"$PWD\" --pidfile=$HOME/celerybeat.pid"
echo "<=="
celery -A gnosisdb.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel $CELERY_LOG_LEVEL --workdir="$PWD" --pidfile=$HOME/celerybeat.pid
