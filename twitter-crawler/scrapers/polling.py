"""
Twitter Scraper to poll last tweets periodically according to a specific query.
"""
import logging
import os
import time
from datetime import datetime

import jsonlines
import tweepy

from .config import create_api

formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()


def get_filename():
    to_json_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.getcwd()
    return path + '/data/polling_' + to_json_timestamp + '.json'


def extract_tweet(tweet):
    try:
        tweet_text = tweet.retweeted_status.full_text
    except AttributeError:
        tweet_text = tweet.full_text
    tweet_dict = {
        'event_id': tweet.id_str,
        'user_id': tweet.user.id,
        'user_name': tweet.user.screen_name,
        'user_description': tweet.user.description,
        'user_location': tweet.user.location,
        'user_following': tweet.user.friends_count,
        'user_followers': tweet.user.followers_count,
        'user_tweets': tweet.user.statuses_count,
        'user_verified': tweet.user.verified,
        'user_creation_timestamp': str(tweet.user.created_at),
        'tweet_id': tweet.id,
        'tweet_text': tweet_text,
        'tweet_retweets': tweet.retweet_count,
        'tweet_likes': tweet.favorite_count,
        'tweet_urls': tweet.entities['urls'],
        'tweet_hashtags': tweet.entities['hashtags'],
        'tweet_user_mentions': tweet.entities['user_mentions'],
        'tweet_source': tweet.source,
        'tweet_timestamp': str(tweet.created_at),
        'tweet_streaming': False
    }
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
        tweets_list.append(extract_tweet(tweet))
        tweets_num += + 1

    end_time = time.time()
    duration_time = round(end_time - start_time, 2)

    logger.info('Number of tweets scraped is {}'.format(tweets_num))
    logger.info('Time taken to complete is {} seconds'.format(duration_time))
    return tweets_list


def export_tweets(tweets):
    filename = get_filename()
    with jsonlines.open(filename, mode='w') as writer:
        writer.write_all(tweets)
    logger.info('Tweets exported to: {}'.format(filename))


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
    search = "url:aljazeera.com OR url:cnn.com OR url:dw.com OR url:foxnews.com OR url:theguardian.com"
    main(search)
