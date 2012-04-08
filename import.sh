export DJANGO_SETTINGS_MODULE=settings
export PYTHONPATH=.:..

LOG="logs/import.log"

python import.py $* 2>> $LOG >> $LOG
