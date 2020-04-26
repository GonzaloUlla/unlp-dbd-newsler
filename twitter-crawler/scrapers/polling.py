"""
Twitter Scraper to poll last tweets periodically according to a specific query.
"""
import time
import json

import jsonlines
import tweepy

from .generators import PollingTweetGenerator
from .sentiments import TweetAnalyzer
from .utils import create_api, get_logger, get_filename

logger = get_logger()


def process_tweet(tweet):
    analyzer = TweetAnalyzer()

    polling_tweet = PollingTweetGenerator(tweet._json).generate()
    sentiments = analyzer.get_sentiment(polling_tweet["tweet_text"])
    polling_tweet.update(sentiments)

    logger.debug("Processed Tweet JSON to export: [{}]".format(json.dumps(polling_tweet)))

    return polling_tweet


def scrap_tweets(api, query, tweets_count):
    start_time = time.time()

    tweepy_cursor = tweepy.Cursor(api.search,
                                  q=query,
                                  lang="en",
                                  tweet_mode='extended')

    cursor_list = [tweet for tweet in tweepy_cursor.items(tweets_count)]
    tweets_list = []
    tweets_num = 0

    for tweet in cursor_list:
        tweets_list.append(process_tweet(tweet))
        tweets_num += + 1

    elapsed_time = round(time.time() - start_time, 2)

    logger.info('{} tweets polled in {} seconds'.format(tweets_num, elapsed_time))
    return tweets_list


def export_tweets(tweets):
    start_time = time.time()

    filename = get_filename('polling')
    with jsonlines.open(filename, mode='w') as writer:
        writer.write_all(tweets)

    elapsed_time = round(time.time() - start_time, 2)
    logger.info('{} polled tweets exported to: {} in {} seconds'.format(len(tweets), filename, elapsed_time))


def main(search_query):
    """Polls Twitter API to scrap and export latest 100 tweets matching a search query."""

    tweets_number = 100  # 100 tweets per request (API MAX LIMIT)
    rounds_number = 10  # Export to file each 10 requests

    logger.info("Starting polling scraper...")
    api = create_api()
    logger.info("Polling {} tweets per request and exporting them each {} requests"
                .format(tweets_number, rounds_number))

    while True:
        tweets_list = []
        for i in range(0, rounds_number):
            tweets_list.extend(scrap_tweets(api, search_query, tweets_number))
        export_tweets(tweets_list)


if __name__ == "__main__":
    search = "url:aljazeera.com OR url:cnn.com OR url:dw.com OR url:foxnews.com OR url:theguardian.com " \
             "OR url:bbc.com OR url:nytimes.com"
    main(search)
