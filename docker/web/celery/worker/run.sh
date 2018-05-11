#!/bin/sh

set -euo pipefail

# DEBUG set in .env
if [ ${DEBUG:-0} = 1 ]; then
    log_level="debug"
else
    log_level="info"
fi

echo "==> Running Celery worker <=="
exec celery worker -A tradingdb.taskapp --loglevel $log_level -c 2