#!/bin/bash

export DJANGO_SETTINGS_MODULE=mofiloterias.settings
export PYTHONPATH=/home/leandro/mofiloterias:/home/leandro

python gamblings/import_worker.py
