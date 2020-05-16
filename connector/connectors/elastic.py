"""
Newsler kafka connector that acts as consumer the newsler-news-crawler and newsler-twitter-crawler.
The information is then pushed to the ElasticSearch indexes.
"""
import logging
import time
import traceback

from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from json import loads
from datetime import datetime
from threading import Thread


formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()

logger.info("Initializing Elastic Search connector")
es = Elasticsearch([{"host": "elasticsearch", "port": 9200}])

class KafkaConsumerElasticSearchPublisher():

    def __init__(self, es_index_prefix=None, kafka_consumer=None, **kwargs):
        self.es_index_prefix = es_index_prefix
        self.kafka_consumer = kafka_consumer

    def consume_and_publish(self):
        es_index = self.es_index_prefix + datetime.today().strftime('%Y%m%d')
        for message in self.consumer:
            try:
                logger.info("Consumed message and publishing to Elastic Search {}".format(str(message.value)))
                message.value['@timestamp'] = int(round(time.time() * 1000))
                es.index(index=es_index, id=message.value['event_id'], body=message.value)
            except Exception as e:
                logger.error("Error Consuming message and publishing {}".format(str(message.value)))
                print(traceback.format_exc())
        time.sleep(30)



class NewsConsumerElasticSearchPublisher(KafkaConsumerElasticSearchPublisher):
    consumer = KafkaConsumer(
        'newsler-news-crawler',
        bootstrap_servers=['kafka:9095'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='newsler-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, **kwargs):
        super().__init__(kafka_consumer=self.consumer,
                         es_index_prefix="news-crawler-",
                         **kwargs)


class TwitterConsumerElasticSearchPublisher(KafkaConsumerElasticSearchPublisher):
    consumer = KafkaConsumer(
        'newsler-twitter-crawler',
        bootstrap_servers=['kafka:9095'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='twitter-group',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, **kwargs):
        super().__init__(kafka_consumer=self.consumer,
                         es_index_prefix="twitter-crawler-",
                         **kwargs)

def main(sleep_time):
    T1 = Thread(target=NewsConsumerElasticSearchPublisher().consume_and_publish, args=())
    T2 = Thread(target=TwitterConsumerElasticSearchPublisher().consume_and_publish, args=())
    T1.start()
    T2.start()
    T1.join()
    T2.join()


if __name__ == "__main__":
    main(30)
