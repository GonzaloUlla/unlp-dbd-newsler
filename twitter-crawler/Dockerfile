FROM python:3.8.2-buster

RUN echo "deb http://ftp.us.debian.org/debian buster main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends logrotate cron enchant && \
    apt-get clean && \
    curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.6.2-amd64.deb && \
    dpkg -i filebeat-7.6.2-amd64.deb && \
    rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    mkdir -p /usr/src/app && \
    mkdir -p /usr/src/app/logs && \
    mkdir -p /usr/src/app/data

COPY filebeat.yml /etc/filebeat/filebeat.yml

WORKDIR /usr/src/app

ADD requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt && \
    python3 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet')"

ADD . /usr/src/app/

RUN chmod 644 scrapers_logs && \
    chown root:root scrapers_logs && \
    cp scrapers_logs /etc/logrotate.d/ && \
    crontab cronjob

ENTRYPOINT ["./entrypoint.sh"]
