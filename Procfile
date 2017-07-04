web: gunicorn --pythonpath "$PWD/gnosisdb" gnosisdb.wsgi:application --log-file=- --access-logfile '-' --log-level info
worker: /bin/sh run_celery.sh