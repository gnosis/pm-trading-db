#!/bin/bash

addgroup celery
useradd -ms /bin/bash celery -g celery

database_status="$(pg_isready -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME)"

case "$database_status" in
  *$ok_response*) >&2 echo "Database available" ;;
  *       )  >&2 echo "GnosisDB database is unavailable - check database status" && exit 1;;
esac

# wait for RabbitMQ server and Postgres to start
echo "==> call run_celery.sh <=="

cd $PWD/gnosisdb
python manage.py migrate --noinput

shutdown() {
    echo "Shuting down gracefully celery"
    kill -3 "$child"
}

trap shutdown SIGTERM SIGINT

echo "==> run worker <=="
celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel info --workdir="$PWD" -c 2 &
child=$!
wait $!
