#!/bin/bash

LOG="logs/mofiloterias.log"
ERRORLOG="logs/errors.log"

echo "######################## START API "`date`" ##########################" >> $LOG
echo "######################## START API "`date`" ##########################" >> $ERRORLOG

export DJANGO_SETTINGS_MODULE=mofiloterias.settings
export PYTHONPATH=.:..

nohup uwsgi -C -s /var/nginx/mofiloterias-uwsgi.sock -i -M -w mofiloterias.wsgi -z 5 -p 10 -l 64 -L -R 10000 -b 8192 --no-orphans --pidfile pid 2>> $ERRORLOG >> $LOG &
