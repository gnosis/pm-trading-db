web: /bin/sh scripts/run_dokku_web.sh
worker: celery -A gnosisdb.apps worker -Q default -n default@%h --loglevel debug -c 1 --workdir /gnosisdb/gnosisdb/
scheduler: celery -A gnosisdb.apps beat -S djcelery.schedulers.DatabaseScheduler --loglevel debug --workdir /gnosisdb/gnosisdb/
