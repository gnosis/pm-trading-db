web: gunicorn --pythonpath "$PWD/gnosisdb" wsgi:application --log-file=- --access-logfile '-' --log-level info
collect: python gnosisdb/manage.py collectstatic
migrate: python gnosisdb/manage.py migrate --noinput
worker: /bin/sh run_celery.sh