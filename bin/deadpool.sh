#!/usr/bin/env bash

source /home/soft/Deadpool/venv/bin/activate
celery -A deadpool worker -B --concurrency=10 --loglevel=ERROR --logfile=/data1/logs/deadpool/deadpool.log
