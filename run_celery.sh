#!/bin/sh

until psql -h "db" -U "postgres" -c '\l'; do
  >&2 echo "GnosisDB database is unavailable - sleeping"
  sleep 1
done


if [ -f "$HOME/var/run/celery/celerybeat.pid" ]; then
    echo "==> Removing celerybeat.pid..."
	rm "$HOME/var/run/celery/celerybeat.pid"
	echo "==> celerybeat.pid removed"
fi

# wait for RabbitMQ server and Postgres to start
echo "==> call run_celery.sh <=="

cd $PWD/gnosisdb

echo "==> run worker <=="
celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel debug --workdir="$PWD" -c 1 &
sleep 10
echo "==> run beat <=="
celery -A gnosisdb.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel debug --workdir="$PWD" --pidfile="$HOME/var/run/celery/celerybeat.pid"
echo "==> run_celery.sh done <=="