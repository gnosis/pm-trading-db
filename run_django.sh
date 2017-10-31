echo "==> Migrating Django <=="
cd $PWD/gnosisdb
python manage.py migrate
python manage.py createcachetable
echo "==> Starting Django Server <=="
python manage.py runserver 0.0.0.0:8000