#!/bin/bash

LOG="logs/import-worker.log"

echo "######################## START WORKER "`date`" ##########################" >> $LOG

export DJANGO_SETTINGS_MODULE=mofiloterias.settings
export PYTHONPATH=/home/leandro/mofiloterias:/home/leandro

python gamblings/import_worker.py 2>> $LOG >> $LOG
