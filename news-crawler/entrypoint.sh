#!/bin/bash

service cron start || exit 1
service filebeat start || exit 1
supervisord -n -c /etc/supervisor/supervisord.conf 2>&1 | tee -a /usr/src/app/logs/supervisor.log &
tail -f /dev/null
