"""
Twitter Scraper to stream tweets in real time according to specific keywords.
"""
from datetime import datetime, timedelta
import json
import logging
import os

import tweepy

from .config import create_api

formatter = '%(levelname)s [%(asctime)s] %(name)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()


def extract_tweet(tweet):
    tweet_dict = {
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
        'tweet_text': tweet.text,
        'tweet_retweets': tweet.retweet_count,
        'tweet_likes': tweet.favorite_count,
        'tweet_urls': tweet.entities['urls'],
        'tweet_hashtags': tweet.entities['hashtags'],
        'tweet_user_mentions': tweet.entities['user_mentions'],
        'tweet_source': tweet.source,
        'tweet_timestamp': str(tweet.created_at)
    }
    return tweet_dict


def get_filename(dt):
    to_json_timestamp = dt.strftime('%Y%m%d_%H%M')
    path = os.getcwd()
    return path + '/stream_' + to_json_timestamp + '.json'


def check_valid_json(dt):
    filename = get_filename(dt)
    last_filename = get_filename(dt - timedelta(minutes=1))
    if not os.path.exists(filename):
        with open(filename, 'a+') as file:
            file.write('[')
        if os.path.exists(last_filename):
            with open(last_filename, 'a+') as file:
                file.write(']')
    else:
        with open(filename, 'a+') as file:
            file.write(',')


def export_tweet(tweet):
    dt = datetime.now()
    check_valid_json(dt)
    filename = get_filename(dt)
    with open(filename, 'a+') as file:
        file.write(json.dumps(extract_tweet(tweet)))
    logger.info('Tweets exported to: {}'.format(filename))


class NewsStreamListener(tweepy.StreamListener):

    def __init__(self, api):
        super().__init__(api)
        self.api = api
        self.me = api.me()

    def on_status(self, tweet):
        print("[{}] New tweet listened on the stream".format(str(datetime.today())))
        print("User name: [{}], Tweet text: [{}]".format(tweet.user.name, tweet.text))
        export_tweet(tweet)

    def on_error(self, status):
        logger.error("Error detected")


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
    main(["aljazeera.com", "cnn.com", "dw.com", "foxnews.com", "theguardian.com"])
