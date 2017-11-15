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

echo "==> run Celery Worker <=="
echo "==> with user: "
whoami
echo "==> Executing command: celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel debug --workdir=\"$PWD\" -c 1"
celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel debug --workdir="$PWD" -c 1
