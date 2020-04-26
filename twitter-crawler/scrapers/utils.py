import logging
import os
from datetime import datetime

import tweepy


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


def get_filename(prefix=''):
    to_json_timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    path = os.getcwd()
    return path + '/data/' + prefix + '_' + to_json_timestamp + '.json'
