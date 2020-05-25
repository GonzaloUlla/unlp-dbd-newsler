"""
Twitter Scraper to poll last tweets periodically according to a specific query.
"""
import time

import tweepy

from .generators import PollingTweetGenerator
from .utils import create_api, get_logger, produce_tweet, process_tweet

logger = get_logger()


def scrap_tweets(api, query, tweets_count):
    start_time = time.time()

    tweepy_cursor = tweepy.Cursor(api.search,
                                  q=query,
                                  lang="en",
                                  tweet_mode='extended')

    cursor_list = [tweet for tweet in tweepy_cursor.items(tweets_count)]
    tweets_num = 0

    for tweet in cursor_list:
        processed_tweet = process_tweet(generated_tweet=PollingTweetGenerator(tweet._json).generate())
        produce_tweet(tweet=processed_tweet, method="polling")
        tweets_num += + 1

    elapsed_time = round(time.time() - start_time, 2)

    logger.info('{} tweets polled in {} seconds'.format(tweets_num, elapsed_time))


def main(search_query):
    """Polls Twitter API to scrap and export latest 100 tweets matching a search query."""

    tweets_number = 100  # 100 tweets per request (API MAX LIMIT)
    rounds_number = 10  # Export to file each 10 requests

    logger.info("Starting polling scraper...")
    api = create_api()
    logger.info("Polling {} tweets per request and exporting them each {} requests"
                .format(tweets_number, rounds_number))

    while True:
        for i in range(0, rounds_number):
            scrap_tweets(api, search_query, tweets_number)


if __name__ == "__main__":
    search = "url:aljazeera.com OR url:cnn.com OR url:dw.com OR url:foxnews.com OR url:theguardian.com " \
             "OR url:bbc.com OR url:nytimes.com"
    main(search)
