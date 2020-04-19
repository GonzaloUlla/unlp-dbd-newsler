"""
Twitter Scraper to poll last tweets periodically according to a specific query.
"""
import time

import jsonlines
import tweepy

from .sentiments import TweetAnalyzer
from .utils import create_api, get_logger, get_filename, extract_tweet

logger = get_logger()


def process_tweet(tweet):
    try:
        tweet_text = tweet.retweeted_status.full_text
    except AttributeError:
        tweet_text = tweet.full_text
    analyzer = TweetAnalyzer()
    tweet_dict = extract_tweet(tweet, tweet_text, streaming=False)
    sentiments = analyzer.get_sentiment(tweet_dict["tweet_text"])
    tweet_dict.update(sentiments)
    return tweet_dict


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
    """Polls Twitter API every 5 seconds to scrap and export latest 100 tweets matching a search query."""

    logger.info("Starting polling scraper...")
    api = create_api()

    tweets_number = 100  # 100 tweets per request (API MAX LIMIT)

    while True:
        tweets_list = []
        for i in range(0, 12):
            tweets_list.extend(scrap_tweets(api, search_query, tweets_number))
            time.sleep(5)  # 5 sec sleep time = 12 requests per minute = 180 requests per 15 minutes (API MAX LIMIT)
        export_tweets(tweets_list)


if __name__ == "__main__":
    search = "url:aljazeera.com OR url:cnn.com OR url:dw.com OR url:foxnews.com OR url:theguardian.com " \
             "OR url:bbc.com OR url:nytimes.com"
    main(search)
