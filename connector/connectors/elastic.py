"""
Newsler's Kafka connector that acts as consumer of topics: newsler-news-crawler and newsler-twitter-crawler.
The information is then pushed to the ElasticSearch indexes.
"""
import logging
import os
import time
import traceback
from datetime import datetime
from json import loads
from threading import Thread

from elasticsearch import Elasticsearch
from kafka import KafkaConsumer

formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()

logger.info("Initializing Elasticsearch connector")
es = Elasticsearch([{"host": os.getenv("ES_HOST", "elasticsearch"), "port": int(os.getenv("ES_PORT", 9200))}])
logger.info("Elasticsearch connector initialized: [{}]".format(repr(es)))


class KafkaConsumerElasticSearchPublisher(object):

    def __init__(self, es_index_prefix=None, kafka_consumer=None, sleep_time=30, **kwargs):
        self.es_index_prefix = es_index_prefix
        self.kafka_consumer = kafka_consumer
        self.sleep_time = sleep_time

    def consume_and_publish(self):
        es_index = self.es_index_prefix + datetime.today().strftime('%Y%m')
        for message in self.kafka_consumer:
            try:
                logger.info("Message consumed, publishing to Elasticsearch: [{}]".format(str(message.value)))
                message.value['@timestamp'] = int(round(time.time() * 1000))
                es.index(index=es_index, id=message.value['event_id'], body=message.value)
            except Exception as e:
                logger.error("Error consuming message and publishing to Elasticsearch: [{}]".format(str(message.value)))
                print(traceback.format_exc())
        time.sleep(self.sleep_time)


class NewsConsumerElasticSearchPublisher(KafkaConsumerElasticSearchPublisher):
    consumer = KafkaConsumer(
        os.getenv("KAFKA_NEWS_TOPIC", "newsler-news-crawler"),
        bootstrap_servers=[os.getenv("KAFKA_ENDPOINT", "kafka:9095")],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='news-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, sleep_time, **kwargs):
        super().__init__(es_index_prefix="news-crawler-",
                         kafka_consumer=self.consumer,
                         sleep_time=sleep_time,
                         **kwargs)


class TwitterConsumerElasticSearchPublisher(KafkaConsumerElasticSearchPublisher):
    consumer = KafkaConsumer(
        os.getenv("KAFKA_TWITTER_TOPIC", "newsler-twitter-crawler"),
        bootstrap_servers=[os.getenv("KAFKA_ENDPOINT", "kafka:9095")],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='twitter-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, sleep_time=30, **kwargs):
        super().__init__(es_index_prefix="twitter-crawler-",
                         kafka_consumer=self.consumer,
                         sleep_time=sleep_time,
                         **kwargs)


def main(sleep_secs):
    T1 = Thread(target=NewsConsumerElasticSearchPublisher(sleep_secs).consume_and_publish, args=())
    T2 = Thread(target=TwitterConsumerElasticSearchPublisher(sleep_secs).consume_and_publish, args=())
    T1.start()
    T2.start()
    T1.join()
    T2.join()


if __name__ == "__main__":
    main(int(os.getenv("CONSUMER_INTERVAL_SECS", 30)))
