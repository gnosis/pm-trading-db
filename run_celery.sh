#!/bin/sh
# wait for RabbitMQ server to start
echo "==> call run_celery.sh <=="
sleep 10
cd gnosisdb/
celery -A django_ether_logs.apps worker -Q default -n default@%h --loglevel debug --workdir="$PWD" -c 1
sleep 10
celery -A django_ether_logs.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel debug --workdir="$PWD"
echo "==> run_celery.sh done <=="