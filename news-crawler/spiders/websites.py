"""
Classes for mews-crawler spiders that scrap news websites. Template Method Design Pattern applied.
"""
import json
import logging
import os
import time
import traceback
from datetime import datetime
from hashlib import sha256

from scrapy.crawler import CrawlerRunner
from scrapy.spiders import Spider
from multiprocessing import Process, Queue
from twisted.internet import reactor
from kafka import KafkaProducer
from json import dumps

formatter = '%(levelname)s [%(asctime)s] %(filename)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=formatter)
logger = logging.getLogger()
topic = 'newsler-news-crawler'

class XPathSpider(Spider):
    """Implements super().parse() as a template method. All mews-crawler
    spiders that use XPath must inherit from this class."""

    def __init__(self, name=None, base_url=None, xpath_list=None, start_urls=None, **kwargs):
        if xpath_list is None:
            xpath_list = []
        if start_urls is None:
            start_urls = [base_url]
        self.base_url = base_url
        self.absolute_url = base_url
        self.start_urls = start_urls
        self.xpath_list = xpath_list
        self.news = {}
        super().__init__(name, **kwargs)

    def parse(self, response):
        for xpath in self.xpath_list:
            for title in response.xpath(xpath):
                self._set_absolute_url(title)
                self.news = {
                    'news_base_url': self._get_base_url(),
                    'news_absolute_url': self._get_absolute_url(),
                    'news_text': self._get_news_text(title)
                }
                self._add_event_id()
                self._produce_news()
                yield self.news

    def _set_absolute_url(self, title):
        self.absolute_url = title.xpath("@href").get()
        if "https" not in self.absolute_url:
            self.absolute_url = self.base_url + self.absolute_url

    def _get_base_url(self):
        return self.base_url

    def _get_absolute_url(self):
        return self.absolute_url

    @staticmethod
    def _get_news_text(title):
        return title.xpath(".//text()").get()

    def _add_event_id(self):
        event_id = sha256(json.dumps(self.news, sort_keys=True).encode('utf8')).hexdigest()
        self.news['event_id'] = event_id

    def _produce_news(self):
        try:
            producer = KafkaProducer(bootstrap_servers=['kafka:9095'],
                                     value_serializer=lambda x:
                                     dumps(x).encode('utf-8'))
            producer.send(topic, value=self.news)
        except Exception as e:
            logger.error("Error producing News {}".format(self.news))
            logger.error(traceback.format_exc())



class AlJazeeraSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="AlJazeera",
                         base_url="https://www.aljazeera.com",
                         xpath_list=["//a//h2[@class='top-sec-title' or @class='top-sec-smalltitle' or "
                                     "@class='topics-sec-item-head']/parent::a"],
                         start_urls=["https://www.aljazeera.com/news"],
                         **kwargs)


class CnnSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="CNN",
                         base_url="https://www.cnn.com",
                         xpath_list=["(//section[@class='zn zn-world-zone-1 zn-left-fluid-right-stack zn--idx-0 "
                                     "zn--ordinary t-light zn-has-two-containers' or @class='zn zn-world-zone-2 "
                                     "zn-balanced zn--idx-1 zn--ordinary t-light zn-has-multiple-containers "
                                     "zn-has-6-containers']//h3[@class='cd__headline']//a)"],
                         start_urls=["https://www.cnn.com/world"],
                         **kwargs)


class DWSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="DW",
                         base_url="https://www.dw.com",
                         xpath_list=["//a//h2[@class='linkable']/parent::a",
                                     "//a//div[@class='teaserContentWrap']//h2/../parent::a"],
                         start_urls=["https://www.dw.com/en/top-stories/world/s-1429"],
                         **kwargs)

    @staticmethod
    def _get_news_text(title):
        return title.xpath(".//child::h2/text()").get().strip('\n')


class FoxNewsSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="FoxNews",
                         base_url="https://www.foxnews.com",
                         xpath_list=["//main[@class='main-content']//h2[@class='title']//a",
                                     "//main[@class='main-content']//h4[@class='title']//a"],
                         start_urls=["https://www.foxnews.com/world"],
                         **kwargs)


class TheGuardianSpider(XPathSpider):
    """Scraps The Guardian website"""

    def __init__(self, **kwargs):
        super().__init__(name="TheGuardian",
                         base_url="https://www.theguardian.com",
                         xpath_list=["(//a[@class='u-faux-block-link"
                                     "__overlay js-headline-text'])"],
                         start_urls=["https://www.theguardian.com/international"],
                         **kwargs)


class BBCSpider(XPathSpider):
    """Scraps The BBC website"""

    def __init__(self, **kwargs):
        super().__init__(name="BBC",
                         base_url="https://www.bbc.com",
                         xpath_list=["//a[@class='gs-c-promo-heading gs-o-faux-block-link__overlay-link "
                                     "gel-paragon-bold nw-o-link-split__anchor']",
                                     "//a[@class='gs-c-promo-heading gs-o-faux-block-link__overlay-link"
                                     " gel-pica-bold nw-o-link-split__anchor']",
                                     "//a[@class='gs-c-promo-heading gs-o-faux-block-link__overlay-link"
                                     " gel-double-pica-bold nw-o-link-split__anchor']"],
                         start_urls=["https://www.bbc.com/news"],
                         **kwargs)


class NYTimesSpider(XPathSpider):
    """Scraps the New York Times website"""

    def __init__(self, **kwargs):
        super().__init__(name="NYTimes",
                         base_url="https://www.nytimes.com",
                         xpath_list=["//h2[@class='css-l2vidh e4e4i5l1']//a",
                                     "//h2[@class='css-y3otqb e134j7ei0']//a",
                                     "//h2[@class='css-1j9dxys e1xfvim30']//a"],
                         start_urls=["https://www.nytimes.com/section/world"],
                         **kwargs)


def run_spider(spider):
    def future(queue):
        try:
            runner = CrawlerRunner()
            deferred = runner.crawl(spider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            queue.put(None)
        except Exception as exception:
            queue.put(exception)

    future_queue = Queue()
    process = Process(target=future, args=(future_queue,))
    process.start()
    result = future_queue.get()
    process.join()

    if result is not None:
        raise result


def main(sleep_time):
    while True:
        run_spider(AlJazeeraSpider)
        run_spider(CnnSpider)
        run_spider(DWSpider)
        run_spider(FoxNewsSpider)
        run_spider(TheGuardianSpider)
        run_spider(BBCSpider)
        run_spider(NYTimesSpider)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main(60)
