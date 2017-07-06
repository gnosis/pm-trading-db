echo "==> Migrating Django models ... "
python gnosisdb/manage.py migrate --noinput
echo "==> Collecting statics ... "
python gnosisdb/manage.py collectstatic
echo "==> Running Gunicorn ... "
gunicorn --pythonpath "$PWD/gnosisdb" wsgi:application --log-file=- --error-logfile=- --access-logfile '-' --log-level info