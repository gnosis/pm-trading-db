echo "==> Migrating Django <=="
# cd $PWD/gnosisdb
python manage.py migrate
echo "==> Starting Django Server <=="
python manage.py runserver 0.0.0.0:8000
