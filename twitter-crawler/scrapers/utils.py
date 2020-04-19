import logging
import os
from datetime import datetime

import tweepy

formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()


def get_logger():
    return logger


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


def get_filename(prefix=''):
    to_json_timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    path = os.getcwd()
    return path + '/data/' + prefix + '_' + to_json_timestamp + '.json'


def extract_entities(entities, attribute):
    return ' '.join(entity[attribute] for entity in entities)


def extract_tweet(tweet, tweet_text=None, streaming=True):
    if tweet_text is None:
        tweet_text = tweet.text
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
        'tweet_urls_list': extract_entities(tweet.entities['urls'], 'expanded_url'),
        'tweet_hashtags': tweet.entities['hashtags'],
        'tweet_hashtags_list': extract_entities(tweet.entities['hashtags'], 'text'),
        'tweet_users_list': extract_entities(tweet.entities['user_mentions'], 'screen_name'),
        'tweet_user_mentions': tweet.entities['user_mentions'],
        'tweet_source': tweet.source,
        'tweet_timestamp': str(tweet.created_at),
        'tweet_streaming': streaming
    }
    return tweet_dict
