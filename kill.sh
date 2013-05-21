#!/bin/bash

LOG="logs/mofiloterias.log"
ERRORLOG="logs/errors.log"

if [[ -e "pid" ]]; then
    echo "######################## KILL API "`date`" ##########################" >> $LOG;
    echo "######################## KILL API "`date`" ##########################" >> $ERRORLOG;

    kill -9 `cat pid`;
fi
