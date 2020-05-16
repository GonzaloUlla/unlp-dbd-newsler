FROM python:3.8.2-buster

RUN echo "deb http://ftp.us.debian.org/debian buster main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends logrotate cron enchant supervisor && \
    apt-get clean && \
    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.6.2-amd64.deb && \
    dpkg -i filebeat-7.6.2-amd64.deb && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/logs && \
    mkdir -p /usr/src/app/data && \
    mkdir -p /usr/src/app/data/archive

WORKDIR /usr/src/app

ADD requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt && \
    python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

ADD . /usr/src/app/

RUN cp filebeat.yml /etc/filebeat/filebeat.yml && \
    chmod go-w /etc/filebeat/filebeat.yml && \
    cat supervisor.conf >> /etc/supervisor/supervisord.conf && \
    chmod 644 logrotate && \
    chown root:root logrotate && \
    cp logrotate /etc/logrotate.d/ && \
    crontab cronjob

RUN rm /etc/localtime && \
    ln -s /usr/share/zoneinfo/America/Argentina/Cordoba /etc/localtime

ENTRYPOINT ["./entrypoint.sh"]
