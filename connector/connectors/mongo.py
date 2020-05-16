"""
Newsler kafka connector that acts as consumer the newsler-news-crawler and newsler-twitter-crawler.
The information is then pushed to the MongoDB collections.
"""
import logging
import time
import traceback

from kafka import KafkaConsumer
from pymongo import MongoClient
from json import loads
from datetime import datetime
from threading import Thread


formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()

logger.info("Initializing MongoDB connector")
mongo = MongoClient('mongo', 27017,  username='root', password='rootpassword')
# Connect to our database
database = mongo['Newsler']

class KafkaConsumerMongoDBPublisher():

    def __init__(self, collection_name=None, kafka_consumer=None, **kwargs):
        self.collection_name = collection_name
        self.kafka_consumer = kafka_consumer

    def consume_and_publish(self):
        collection = database[self.collection_name]
        for message in self.consumer:
            try:
                logger.info("Consumed message and publishing to MongoDB {}".format(str(message.value)))
                message.value['timestamp'] = int(round(time.time() * 1000))
                message.value['_id'] = message.value['event_id']
                doc_id = collection.insert_one(message.value).inserted_id
                logger.info("Inserted record in MongoDB {}".format(doc_id))
            except Exception as e:
                logger.error("Error Consuming message and publishing to MongoDB {}".format(str(message.value)))
                print(traceback.format_exc())
        time.sleep(30)


class NewsConsumerMongoDBPublisher(KafkaConsumerMongoDBPublisher):
    consumer = KafkaConsumer(
        'newsler-news-crawler',
        bootstrap_servers=['kafka:9095'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='newsler-group-mongo',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, **kwargs):
        super().__init__(collection_name="news-crawler",
                         kafka_consumer=self.consumer,
                         **kwargs)


class TwitterConsumerMongoDBPublisher(KafkaConsumerMongoDBPublisher):
    consumer = KafkaConsumer(
        'newsler-twitter-crawler',
        bootstrap_servers=['kafka:9095'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='twitter-group-mongo',
        value_deserializer=lambda x: loads(x.decode('utf-8')))

    def __init__(self, **kwargs):
        super().__init__(collection_name="twitter-crawler",
                         kafka_consumer=self.consumer,
                         **kwargs)

def main(sleep_time):
    T1 = Thread(target=NewsConsumerMongoDBPublisher().consume_and_publish, args=())
    T2 = Thread(target=TwitterConsumerMongoDBPublisher().consume_and_publish, args=())
    T1.start()
    T2.start()
    T1.join()
    T2.join()


if __name__ == "__main__":
    main(30)
