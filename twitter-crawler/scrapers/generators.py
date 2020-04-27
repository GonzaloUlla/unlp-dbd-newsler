import json
import time

from .utils import get_logger
from .extractors import AttributeExtractor, EntitiesExtractor, EntitiesListExtractor, RetweetedStatusExtractor, \
    QuotedStatusExtractor

logger = get_logger()

retweeted_status_str = "retweeted_status"


class Generator(object):

    def generate(self):
        logger.error("NotImplementedError: {}.generate callback is not defined".format(self.__class__.__name__))
        raise NotImplementedError("{}.generate callback is not defined".format(self.__class__.__name__))


class PollingTweetTextGenerator(Generator):

    def __init__(self, tweet=None, nested_extractor=None):
        if tweet is None:
            logger.error("ValueError: Tweet cannot be None")
            raise ValueError("Tweet must be a Tweepy Status JSON object")
        if nested_extractor is None:
            nested_extractor = RetweetedStatusExtractor(tweet)
        self.tweet = tweet
        self.nested_extractor = nested_extractor

    def generate(self):
        return self.nested_extractor.extract("full_text", self.tweet["full_text"])


class StreamingTweetTextGenerator(Generator):

    def __init__(self, tweet=None, nested_extractor=None):
        if tweet is None:
            logger.error("ValueError: Tweet cannot be None")
            raise ValueError("Tweet must be a Tweepy Status JSON object")
        if nested_extractor is None:
            nested_extractor = RetweetedStatusExtractor(tweet)
        self.tweet = tweet
        self.nested_extractor = nested_extractor

    def generate(self):
        truncated = self.nested_extractor.extract("truncated")
        if truncated:
            tweet_text = self.nested_extractor.extract("extended_tweet")["full_text"]
        elif truncated is not None:
            tweet_text = self.nested_extractor.extract("text")
        elif "extended_tweet" in self.tweet:
            tweet_text = self.tweet["extended_tweet"]["full_text"]
        else:
            tweet_text = self.tweet["text"]
        return tweet_text


class AtomicTweetGenerator(Generator):

    def __init__(self, tweet=None, text_generator=None, streaming=False, retweeted_status=None):
        if text_generator is None:
            text_generator = PollingTweetTextGenerator(tweet)
        if retweeted_status is None:
            retweeted_status = retweeted_status_str
        self.tweet = tweet
        self.text_generator = text_generator
        self.streaming = streaming
        self.retweeted_status = retweeted_status
        self.tweet_attr_extractor = AttributeExtractor(tweet)
        self.entities_attr_extractor = AttributeExtractor(tweet["entities"])

    def generate(self):
        atomic_tweet = {
            "event_id": self.tweet_attr_extractor.extract("id_str"),
            "tweet_id": self.tweet_attr_extractor.extract("id"),
            "tweet_id_str": self.tweet_attr_extractor.extract("id_str"),
            "tweet_text": self.text_generator.generate(),
            "tweet_hashtags": self.entities_attr_extractor.extract("hashtags"),
            "tweet_is_quote": self.tweet_attr_extractor.extract("is_quote_status"),
            "tweet_is_retweet": self.retweeted_status in self.tweet,
            "tweet_lang": self.tweet_attr_extractor.extract("lang"),
            "tweet_likes": self.tweet_attr_extractor.extract("favorite_count"),
            "tweet_mentions": self.entities_attr_extractor.extract("user_mentions"),
            "tweet_retweets": self.tweet_attr_extractor.extract("retweet_count"),
            "tweet_source": self.tweet_attr_extractor.extract("source"),
            "tweet_streaming": self.streaming,
            "tweet_timestamp": str(self.tweet_attr_extractor.extract("created_at")),
            "tweet_urls": self.entities_attr_extractor.extract("urls")
        }
        return atomic_tweet


class UserGenerator(Generator):

    def __init__(self, tweet=None):
        if tweet is None:
            logger.error("ValueError: Tweet cannot be None")
            raise ValueError("Tweet must be a Tweepy Status JSON object")
        self.user_extractor = AttributeExtractor(tweet["user"])

    def generate(self):
        user = {
            "tweet_user_id": self.user_extractor.extract("id"),
            "tweet_user_name": self.user_extractor.extract("screen_name"),
            "tweet_user_creation_timestamp": str(self.user_extractor.extract("created_at")),
            "tweet_user_description": self.user_extractor.extract("description"),
            "tweet_user_followers": self.user_extractor.extract("followers_count"),
            "tweet_user_following": self.user_extractor.extract("friends_count"),
            "tweet_user_location": self.user_extractor.extract("location"),
            "tweet_user_tweets": self.user_extractor.extract("statuses_count"),
            "tweet_user_verified": self.user_extractor.extract("verified")
        }
        return user


class RetweetedTweetGenerator(Generator):

    def __init__(self, tweet=None, text_generator=None):
        if text_generator is None:
            text_generator = PollingTweetTextGenerator(tweet, RetweetedStatusExtractor(tweet))
        self.text_generator = text_generator
        self.retweeted_extractor = RetweetedStatusExtractor(tweet)
        self.entities_attr_extractor = AttributeExtractor(self.retweeted_extractor.extract("entities"))
        self.user_attr_extractor = AttributeExtractor(self.retweeted_extractor.extract("user"))

    def _get_retweeted_text(self):
        return self.text_generator.generate() if self.retweeted_extractor.extract("id_str") else None

    def generate(self):
        retweeted_tweet = {
            "tweet_retweeted_id": self.retweeted_extractor.extract("id"),
            "tweet_retweeted_id_str": self.retweeted_extractor.extract("id_str"),
            "tweet_retweeted_text": self._get_retweeted_text(),
            "tweet_retweeted_hashtags": self.entities_attr_extractor.extract("hashtags"),
            "tweet_retweeted_likes": self.retweeted_extractor.extract("favorite_count"),
            "tweet_retweeted_mentions": self.entities_attr_extractor.extract("user_mentions"),
            "tweet_retweeted_retweets": self.retweeted_extractor.extract("retweet_count"),
            "tweet_retweeted_urls": self.entities_attr_extractor.extract("urls"),
            "tweet_retweeted_user_id": self.user_attr_extractor.extract("id"),
            "tweet_retweeted_user_name": self.user_attr_extractor.extract("screen_name")
        }
        return retweeted_tweet


class QuotedTweetGenerator(Generator):

    def __init__(self, tweet=None, text_generator=None):
        if text_generator is None:
            text_generator = PollingTweetTextGenerator(tweet, QuotedStatusExtractor(tweet))
        self.text_generator = text_generator
        self.quoted_extractor = QuotedStatusExtractor(tweet)
        self.entities_attr_extractor = AttributeExtractor(self.quoted_extractor.extract("entities"))
        self.user_attr_extractor = AttributeExtractor(self.quoted_extractor.extract("user"))

    def _get_quoted_text(self):
        return self.text_generator.generate() if self.quoted_extractor.extract("id_str") else None

    def generate(self):
        quoted_tweet = {
            "tweet_quoted_id": self.quoted_extractor.extract("id"),
            "tweet_quoted_id_str": self.quoted_extractor.extract("id_str"),
            "tweet_quoted_text": self._get_quoted_text(),
            "tweet_quoted_hashtags": self.entities_attr_extractor.extract("hashtags"),
            "tweet_quoted_likes": self.quoted_extractor.extract("favorite_count"),
            "tweet_quoted_mentions": self.entities_attr_extractor.extract("user_mentions"),
            "tweet_quoted_retweets": self.quoted_extractor.extract("retweet_count"),
            "tweet_quoted_urls": self.entities_attr_extractor.extract("urls"),
            "tweet_quoted_user_id": self.user_attr_extractor.extract("id"),
            "tweet_quoted_user_name": self.user_attr_extractor.extract("screen_name")
        }
        return quoted_tweet


class TweetListsGenerator(Generator):

    def __init__(self, base_tweet=None):
        if base_tweet is None:
            logger.error("ValueError: base_tweet cannot be None")
            raise ValueError("A base_tweet is required")
        self.tweet_ext = AttributeExtractor(base_tweet)

    def _get_entity_attr(self, k, v):
        return EntitiesExtractor(self.tweet_ext.extract(k)).extract(v)

    def generate(self):
        tweet_lists = {
            "tweet_hashtags_list": self._get_entity_attr("tweet_hashtags", "text"),
            "tweet_mentions_list": self._get_entity_attr("tweet_mentions", "screen_name"),
            "tweet_urls_list": self._get_entity_attr("tweet_urls", "expanded_url"),
            "tweet_retweeted_hashtags_list": self._get_entity_attr("tweet_retweeted_hashtags", "text"),
            "tweet_retweeted_mentions_list": self._get_entity_attr("tweet_retweeted_mentions", "screen_name"),
            "tweet_retweeted_urls_list": self._get_entity_attr("tweet_retweeted_urls", "expanded_url"),
            "tweet_quoted_hashtags_list": self._get_entity_attr("tweet_quoted_hashtags", "text"),
            "tweet_quoted_mentions_list": self._get_entity_attr("tweet_quoted_mentions", "screen_name"),
            "tweet_quoted_urls_list": self._get_entity_attr("tweet_quoted_urls", "expanded_url")
        }
        return tweet_lists


class TweetAllListsGenerator(Generator):

    def __init__(self, tweet_with_lists=None):
        if tweet_with_lists is None:
            logger.error("ValueError: tweet_with_lists cannot be None")
            raise ValueError("A tweet_with_lists is required")
        self.tweet_ext = AttributeExtractor(tweet_with_lists)

    def generate(self):
        hashtags_list = [self.tweet_ext.extract("tweet_hashtags_list"),
                         self.tweet_ext.extract("tweet_retweeted_hashtags_list"),
                         self.tweet_ext.extract("tweet_quoted_hashtags_list")]

        mentions_list = [self.tweet_ext.extract("tweet_mentions_list"),
                         self.tweet_ext.extract("tweet_retweeted_mentions_list"),
                         self.tweet_ext.extract("tweet_quoted_mentions_list")]

        urls_list = [self.tweet_ext.extract("tweet_urls_list"),
                     self.tweet_ext.extract("tweet_retweeted_urls_list"),
                     self.tweet_ext.extract("tweet_quoted_urls_list")]

        tweet_all_lists = {
            "tweet_hashtags_list_all": EntitiesListExtractor().extract(hashtags_list),
            "tweet_mentions_list_all": EntitiesListExtractor().extract(mentions_list),
            "tweet_urls_list_all": EntitiesListExtractor().extract(urls_list)
        }

        return tweet_all_lists


class PollingTweetGenerator(Generator):

    def __init__(self, tweet=None):
        self.tweet = tweet
        self.atomic = AtomicTweetGenerator(tweet)
        self.user = UserGenerator(tweet)
        self.retweeted = RetweetedTweetGenerator(tweet)
        self.quoted = QuotedTweetGenerator(tweet)

    def generate(self):
        logger.debug("Generating polling tweet from JSON: [{}]".format(json.dumps(self.tweet)))
        start_time = time.time()

        polling_tweet = self.atomic.generate()
        polling_tweet.update(self.user.generate())
        polling_tweet.update(self.retweeted.generate())
        polling_tweet.update(self.quoted.generate())
        polling_tweet.update(TweetListsGenerator(polling_tweet).generate())
        polling_tweet.update(TweetAllListsGenerator(polling_tweet).generate())

        elapsed_time = round(time.time() - start_time, 4)
        logger.debug("Generated polling tweet in {} seconds: [{}]".format(elapsed_time, json.dumps(polling_tweet)))
        return polling_tweet


class StreamingTweetGenerator(Generator):

    def __init__(self, tweet=None):
        self.tweet = tweet
        self.atomic = AtomicTweetGenerator(tweet, text_generator=StreamingTweetTextGenerator(tweet), streaming=True)
        self.user = UserGenerator(tweet)
        self.retweeted = RetweetedTweetGenerator(tweet, text_generator=StreamingTweetTextGenerator(tweet))
        qse = QuotedStatusExtractor(tweet)
        self.quoted = QuotedTweetGenerator(tweet, text_generator=StreamingTweetTextGenerator(tweet, qse))

    def generate(self):
        logger.debug("Generating streaming tweet from JSON: [{}]".format(json.dumps(self.tweet)))
        start_time = time.time()

        streaming_tweet = self.atomic.generate()
        streaming_tweet.update(self.user.generate())
        streaming_tweet.update(self.retweeted.generate())
        streaming_tweet.update(self.quoted.generate())
        streaming_tweet.update(TweetListsGenerator(streaming_tweet).generate())
        streaming_tweet.update(TweetAllListsGenerator(streaming_tweet).generate())

        elapsed_time = round(time.time() - start_time, 4)
        logger.debug("Generated streaming tweet in {} seconds: [{}]".format(elapsed_time, json.dumps(streaming_tweet)))
        return streaming_tweet
