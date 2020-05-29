#!/bin/bash

/usr/src/app/wait-for-it.sh kafka:9095 || exit 2
/usr/src/app/wait-for-it.sh elasticsearch:9200 || exit 2

echo "Putting default index template..."
curl -X PUT "elasticsearch:9200/_template/default?pretty" -H 'Content-Type: application/json' \
  -d @/usr/src/app/elasticsearch-template.json

service cron start || exit 2
service filebeat start || exit 2
supervisord -n -c /etc/supervisor/supervisord.conf 2>&1 | tee -a /usr/src/app/logs/supervisor.log &
tail -f /dev/null
