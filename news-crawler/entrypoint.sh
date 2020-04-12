#!/bin/bash

service cron start
service filebeat start
cd /usr/src/app || exit 1
nohup python -m spiders.websites spiders/websites.py 2>&1 | tee -a logs/websites.log &
tail -f /dev/null
