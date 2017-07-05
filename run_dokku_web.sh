python gnosisdb/manage.py migrate --noinput
python gnosisdb/manage.py collectstatic
gunicorn --pythonpath "$PWD/gnosisdb" wsgi:application --log-file=- --error-logfile=- --access-logfile '-' --log-level info