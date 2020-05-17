FROM wurstmeister/kafka

RUN rm /etc/localtime && \
    ln -s /usr/share/zoneinfo/America/Argentina/Cordoba /etc/localtime

ENTRYPOINT ["./entrypoint.sh"]
