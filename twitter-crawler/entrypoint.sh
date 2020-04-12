#!/bin/bash

service cron start
service filebeat start
cd /usr/src/app || exit 1
nohup python -m scrapers.polling scrapers/polling.py 2>&1 | tee -a logs/polling.log &
nohup python -m scrapers.streaming scrapers/streaming.py 2>&1 | tee -a logs/streaming.log &
tail -f /dev/null
