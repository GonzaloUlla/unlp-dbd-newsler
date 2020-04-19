import re
import time
from string import punctuation

import enchant
from nltk.corpus import stopwords, wordnet
from nltk.metrics import edit_distance
from nltk.tokenize import word_tokenize
from textblob import TextBlob

from .utils import get_logger

logger = get_logger()

replacement_patterns = [
    (r'((www\.[^\s]+)|(https?://[^\s]+))', 'URL'),
    (r'@[^\s]+', 'AT_USER'),
    (r'#([^\s]+)', r'\1')
]

stopwords_list = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])


class Replacer(object):

    def replace(self, text):
        raise NotImplementedError('{}.replace callback is not defined'.format(self.__class__.__name__))


class RegexReplacer(Replacer):

    def __init__(self, patterns=None):
        if patterns is None:
            patterns = replacement_patterns
        self.patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]

    def replace(self, text):
        s = text
        for (pattern, repl) in self.patterns:
            s = re.sub(pattern, repl, s)
        return s


class RepeatReplacer(Replacer):

    def __init__(self):
        self.repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
        self.repl = r'\1\2\3'

    def replace(self, word):
        if wordnet.synsets(word):
            return word

        repl_word = self.repeat_regexp.sub(self.repl, word)

        if repl_word != word:
            return self.replace(repl_word)
        else:
            return repl_word


class SpellingReplacer(Replacer):

    def __init__(self, dict_name='en', max_dist=2):
        self.spell_dict = enchant.Dict(dict_name)
        self.max_dist = max_dist

    def replace(self, word):
        if self.spell_dict.check(word):
            return word

        suggestions = self.spell_dict.suggest(word)

        if suggestions and edit_distance(word, suggestions[0]) <= self.max_dist:
            return suggestions[0]
        else:
            return word


class TweetReplacer(Replacer):

    def __init__(self):
        self.stopwords = stopwords_list
        self.regex_replacer = RegexReplacer()
        self.repeat_replacer = RepeatReplacer()
        self.spelling_replacer = SpellingReplacer()

    def replace(self, tweet):
        tweet = self.regex_replacer.replace(tweet.lower())
        tweet = [self.repeat_replacer.replace(word) for word in word_tokenize(tweet)]
        tweet = [self.spelling_replacer.replace(word) for word in tweet if word not in self.stopwords]
        tweet = ' '.join(word for word in tweet if word not in self.stopwords)
        logger.debug("Replaced tweet text to: [{}]".format(tweet))
        return tweet


class TweetAnalyzer(object):

    def __init__(self):
        self.replacer = TweetReplacer()

    def get_sentiment(self, tweet_text):
        start_time = time.time()
        logger.debug("Analyzing sentiments for tweet text: [{}]".format(tweet_text))
        analysis = TextBlob(self.replacer.replace(tweet_text))

        tweet_sentiment = {'tweet_sentiment_polarity': analysis.sentiment.polarity,
                           'tweet_sentiment_subjectivity': analysis.sentiment.subjectivity,
                           'tweet_sentiment_label': 'positive' if analysis.sentiment.polarity > 0
                           else 'neutral' if analysis.sentiment.polarity == 0 else 'negative'}

        elapsed_time = time.time() - start_time
        logger.debug("Tweet sentiments analyzed in {} seconds: [{}]".format(round(elapsed_time, 2),
                                                                            str(tweet_sentiment)))
        return tweet_sentiment
