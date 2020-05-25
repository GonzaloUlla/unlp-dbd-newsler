"""
Twitter Scraper to stream tweets in real time according to specific keywords.
"""
import tweepy

from .generators import StreamingTweetGenerator
from .utils import create_api, get_logger, produce_tweet, process_tweet

logger = get_logger()


class NewsStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        logger.info("New tweet streamed with text: [{}]".format(tweet.text[:50] + "..."))
        processed_tweet = process_tweet(generated_tweet=StreamingTweetGenerator(tweet._json).generate())
        produce_tweet(tweet=processed_tweet, method="streaming")

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
