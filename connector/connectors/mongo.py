"""
Newsler's Kafka connector that acts as consumer of topics: newsler-news-crawler and newsler-twitter-crawler.
The information is then pushed to the MongoDB collections.
"""
import logging
import os
import time
import traceback
from json import loads
from threading import Thread

from kafka import KafkaConsumer
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

logging_level = os.getenv("LOGGING_LEVEL", "INFO")
formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.getLevelName(logging_level), format=formatter)
logger = logging.getLogger()

logger.info("Initializing MongoDB connector")
mongo = MongoClient(os.getenv("MONGO_HOST", "mongo"), int(os.getenv("MONGO_PORT", 27017)),
                    username=os.getenv("MONGO_USERNAME", "root"), password=os.getenv("MONGO_PASSWORD", "rootpassword"))
database = mongo[os.getenv("MONGO_DATABASE", "newsler")]
logger.info("MongoDB connector initialized: [{}]".format(repr(mongo)))


class KafkaConsumerMongoDBPublisher(object):

    def __init__(self, collection_name=None, kafka_consumer=None, sleep_time=30, **kwargs):
        self.collection_name = collection_name
        self.kafka_consumer = kafka_consumer
        self.sleep_time = sleep_time

    def consume_and_publish(self):
        collection = database[self.collection_name]
        for message in self.kafka_consumer:
            try:
                logger.info("Message consumed, publishing to MongoDB: [{}]".format(str(message.value)))
                message.value['timestamp'] = int(round(time.time() * 1000))
                message.value['_id'] = message.value['event_id']
                doc_id = collection.insert_one(message.value).inserted_id
                logger.info("Record inserted in MongoDB: [{}]".format(doc_id))
            except DuplicateKeyError as dke:
                logger.error(
                    "Error inserting record in MongoDB, record exists: [{}]".format(str(message.value['event_id'])))
            except Exception as e:
                logger.error("Error consuming message and publishing to MongoDB: [{}]".format(str(message.value)))
                print(traceback.format_exc())
        time.sleep(self.sleep_time)


class NewsConsumerMongoDBPublisher(KafkaConsumerMongoDBPublisher):
    consumer = KafkaConsumer(
        os.getenv("KAFKA_NEWS_TOPIC", "newsler-news-crawler"),
        bootstrap_servers=[os.getenv("KAFKA_ENDPOINT", "kafka:9095")],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="news-group-mongo",
        value_deserializer=lambda x: loads(x.decode("utf-8")))

    def __init__(self, sleep_time=30, **kwargs):
        super().__init__(collection_name="news-crawler",
                         kafka_consumer=self.consumer,
                         sleep_time=sleep_time,
                         **kwargs)


class TwitterConsumerMongoDBPublisher(KafkaConsumerMongoDBPublisher):
    consumer = KafkaConsumer(
        os.getenv("KAFKA_TWITTER_TOPIC", "newsler-twitter-crawler"),
        bootstrap_servers=[os.getenv("KAFKA_ENDPOINT", "kafka:9095")],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="twitter-group-mongo",
        value_deserializer=lambda x: loads(x.decode("utf-8")))

    def __init__(self, sleep_time=30, **kwargs):
        super().__init__(collection_name="twitter-crawler",
                         kafka_consumer=self.consumer,
                         sleep_time=sleep_time,
                         **kwargs)


def main(sleep_secs):
    T1 = Thread(target=NewsConsumerMongoDBPublisher(sleep_secs).consume_and_publish, args=())
    T2 = Thread(target=TwitterConsumerMongoDBPublisher(sleep_secs).consume_and_publish, args=())
    T1.start()
    T2.start()
    T1.join()
    T2.join()


if __name__ == "__main__":
    main(int(os.getenv("CONSUMER_INTERVAL_SECS", 30)))
