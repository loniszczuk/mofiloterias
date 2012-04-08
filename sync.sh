#!/bin/bash

rsync -rlpgoDhLvc --delete --exclude "settings.py" --exclude "- *.pyc" --exclude "- *.pid" --exclude "- *.log" --exclude "- pid" --exclude "- .git" --exclude 'db' . lonis:mofiloterias/
