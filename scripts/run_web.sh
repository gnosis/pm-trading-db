#!/bin/sh
echo "==> Migrating Django models ... "
python gnosisdb/manage.py migrate --noinput
echo "==> Collecting statics ... "
DOCKER_SHARED_DIR=/gnosis-nginx
rm -rf $DOCKER_SHARED_DIR/*
STATIC_ROOT=$DOCKER_SHARED_DIR/staticfiles python gnosisdb/manage.py collectstatic
echo "==> Running Gunicorn ... "
gunicorn --pythonpath "$PWD/gnosisdb" wsgi:application --log-file=- --error-logfile=- --access-logfile '-' --log-level info -b unix:$DOCKER_SHARED_DIR/gunicorn.socket --worker-class gevent
