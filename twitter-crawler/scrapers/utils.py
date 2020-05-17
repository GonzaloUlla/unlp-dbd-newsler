import logging
import os
import traceback
from datetime import datetime

import tweepy
from kafka import KafkaProducer
from .sentiments import TweetAnalyzer
from json import dumps


def get_logger():
    logging_level = os.getenv("LOGGING_LEVEL", "INFO")
    formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
    logging.basicConfig(level=logging.getLevelName(logging_level), format=formatter)
    return logging.getLogger()


logger = get_logger()


def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    logger.debug("Creating Tweepy API...")
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        logger.debug("Verifying Tweepy API credentials...")
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating Tweepy API", exc_info=True)
        raise e
    logger.info("Tweepy API created successfully")
    return api


def produce_tweet(tweet=None, method=None):
    try:
        producer = KafkaProducer(bootstrap_servers=['kafka:9095'],
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))
        logger.info("Producing {crawler} tweet: {data}".format(crawler=method, data=str(tweet)))
        producer.send(topic='newsler-twitter-crawler', value=tweet)
    except Exception as e:
        logger.error("Error producing {crawler} tweet: {data} \n {exc}"
        .format(crawler=method, data=str(tweet), exc=traceback.format_exc()))


def process_tweet(generated_tweet=None):
    analyzer = TweetAnalyzer()

    sentiments = analyzer.get_sentiment(generated_tweet["tweet_text"])
    generated_tweet.update(sentiments)

    logger.debug("Processed Tweet JSON to export: [{}]".format(dumps(generated_tweet)))
    return generated_tweet
