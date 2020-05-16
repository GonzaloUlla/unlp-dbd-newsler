"""
Twitter Scraper to stream tweets in real time according to specific keywords.
"""
import json
import tweepy
import time
import traceback

from .generators import StreamingTweetGenerator
from .sentiments import TweetAnalyzer
from .utils import create_api, get_filename, get_logger
from kafka import KafkaProducer
from json import dumps
from json import loads

logger = get_logger()
topic = 'newsler-twitter-crawler'


def process_tweet(tweet):
    analyzer = TweetAnalyzer()

    streaming_tweet = StreamingTweetGenerator(tweet._json).generate()
    sentiments = analyzer.get_sentiment(streaming_tweet["tweet_text"])
    streaming_tweet.update(sentiments)

    logger.debug("Processed Tweet JSON to export: [{}]".format(json.dumps(streaming_tweet)))

    return streaming_tweet


def export_tweet(tweet):
    filename = get_filename('streaming')
    with open(filename, 'a+') as file:
        file.write(json.dumps(process_tweet(tweet)) + '\n')
    logger.debug('Tweet exported to: {}'.format(filename))


def produce_tweet(tweet):
    try:
        producer = KafkaProducer(bootstrap_servers=['kafka:9095'],
                                 value_serializer=lambda x:
                                 dumps(x).encode('utf-8'))
        logger.info("Producing streaming tweet {}".format(str(tweet)))
        producer.send(topic, value=tweet)
    except Exception as e:
        logger.error("Error producing streaming tweet {}".format(str(tweet)))
        logger.error(traceback.format_exc())


class NewsStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        logger.info("New tweet streamed with text: [{}]".format(tweet.text[:50] + "..."))
        #export_tweet(tweet)
        produce_tweet(process_tweet(tweet))

    def on_error(self, status):
        logger.error("Error detected")
        logger.error("Error: [{}]".format(status))


def listen_stream(api, keywords):
    logger.info("Listening for keywords: {} in the stream ".format(str(keywords)))
    tweets_listener = NewsStreamListener(api)
    stream = tweepy.Stream(api.auth, tweets_listener)
    stream.filter(track=keywords, languages=["en"])


def main(keywords):
    logger.info("Starting streaming scraper...")
    api = create_api()
    listen_stream(api, keywords)


if __name__ == "__main__":
    main(["aljazeera.com", "cnn.com", "dw.com", "foxnews.com", "theguardian.com", "bbc.com", "nytimes.com"])
