FROM python:3.8.2-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends logrotate cron && \
    apt-get clean && \
    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.6.2-amd64.deb && \
    dpkg -i filebeat-7.6.2-amd64.deb && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/logs && \
    mkdir -p /usr/src/app/json

COPY filebeat.yml /etc/filebeat/filebeat.yml

WORKDIR /usr/src/app

ADD requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

ADD . /usr/src/app/

RUN chmod 644 spiders_logs && \
    chown root:root spiders_logs && \
    cp spiders_logs /etc/logrotate.d/ && \
    crontab cronjob

CMD service cron start && service filebeat start && tail -f /dev/null
