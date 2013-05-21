#!/bin/bash

LOG="logs/import-worker.log"
ERRORLOG="logs/import-worker-errors.log"

echo "######################## START WORKER "`date`" ##########################" >> $LOG
echo "######################## START WORKER "`date`" ##########################" >> $ERRORLOG

export DJANGO_SETTINGS_MODULE=mofiloterias.settings
export PYTHONPATH=.:..

nohup python gamblings/import_worker.py 2>> $ERRORLOG >> $LOG &
echo $! > worker.pid