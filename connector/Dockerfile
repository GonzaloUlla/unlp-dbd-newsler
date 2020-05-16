FROM python:3.8.2-buster

RUN apt-get update && \
    apt-get install -y --no-install-recommends logrotate cron supervisor && \
    apt-get clean && \
    mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/logs && \
    mkdir -p /usr/src/app/data && \
    mkdir -p /usr/src/app/data/archive

WORKDIR /usr/src/app

ADD requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

ADD . /usr/src/app/

RUN cat supervisor.conf >> /etc/supervisor/supervisord.conf && \
    chmod 644 logrotate && \
    chown root:root logrotate && \
    cp logrotate /etc/logrotate.d/ && \
    crontab cronjob

RUN rm /etc/localtime && \
    ln -s /usr/share/zoneinfo/America/Argentina/Cordoba /etc/localtime

ENTRYPOINT ["./entrypoint.sh"]
