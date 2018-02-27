web: /bin/sh scripts/run_dokku_web.sh
worker: celery -A gnosisdb.taskapp worker -Q default -n default@%h --loglevel debug -c 1 --workdir /gnosisdb/gnosisdb/
scheduler: celery -A gnosisdb.taskapp beat -S djcelery.schedulers.DatabaseScheduler --loglevel debug --workdir /gnosisdb/gnosisdb/
