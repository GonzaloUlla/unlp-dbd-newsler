"""
Twitter Scraper to stream tweets in real time according to specific keywords.
"""
import json

import tweepy

from .sentiments import TweetAnalyzer
from .utils import create_api, get_logger, get_filename, extract_tweet

logger = get_logger()


def process_tweet(tweet):
    analyzer = TweetAnalyzer()
    tweet_dict = extract_tweet(tweet)
    sentiments = analyzer.get_sentiment(tweet_dict["tweet_text"])
    tweet_dict.update(sentiments)
    return tweet_dict


def export_tweet(tweet):
    filename = get_filename('streaming')
    with open(filename, 'a+') as file:
        file.write(json.dumps(process_tweet(tweet)) + '\n')
    logger.debug('Tweet exported to: {}'.format(filename))


class NewsStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        logger.info("New tweet streamed with text: [{}]".format(tweet.text[:50] + "..."))
        export_tweet(tweet)

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
