#!/bin/bash

/usr/src/app/wait-for-it.sh logstash:9600 || exit 2
service cron start || exit 2
service filebeat start || exit 2
supervisord -n -c /etc/supervisor/supervisord.conf 2>&1 | tee -a /usr/src/app/logs/supervisor.log &
tail -f /dev/null
