"""
Classes for mews-crawler spiders that scrap news websites. Template Method Design Pattern applied.
"""
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Spider


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
        super().__init__(name, **kwargs)

    def parse(self, response):
        for xpath in self.xpath_list:
            for title in response.xpath(xpath):
                self._set_absolute_url(title)
                yield {
                    'news_timestamp': _get_timestamp(),
                    'news_base_url': self._get_base_url(),
                    'news_absolute_url': self._get_absolute_url(),
                    'news_text': self._get_news_text(title)
                }

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


def _get_timestamp():
    return str(datetime.now())


class AlJazeeraSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="AlJazeera",
                         base_url="https://www.aljazeera.com",
                         xpath_list=["//a//h2[@class='top-sec-title' or @class='top-sec-smalltitle' or "
                                     "@class='topics-sec-item-head']/parent::a"],
                         start_urls=["https://www.aljazeera.com/news"])


class CnnSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="CNN",
                         base_url="https://www.cnn.com/world",
                         xpath_list=["(//section[@class='zn zn-world-zone-1 zn-left-fluid-right-stack zn--idx-0 "
                                     "zn--ordinary t-light zn-has-two-containers' or @class='zn zn-world-zone-2 "
                                     "zn-balanced zn--idx-1 zn--ordinary t-light zn-has-multiple-containers "
                                     "zn-has-6-containers']//h3[@class='cd__headline']//a)"],
                         **kwargs)

    def _set_absolute_url(self, title):
        self.absolute_url = title.xpath("@href").get()
        if "https" not in self.absolute_url:
            self.absolute_url = self.base_url + str(self.absolute_url)


class DWSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="DW",
                         base_url="https://www.dw.com/en/top-stories/world/s-1429",
                         xpath_list=["//a//h2[@class='linkable']/parent::a",
                                     "//a//div[@class='teaserContentWrap']//h2/../parent::a"],
                         **kwargs)

    @staticmethod
    def _get_news_text(title):
        return title.xpath(".//child::h2/text()").get().strip('\n')


class FoxNewsSpider(XPathSpider):

    def __init__(self, **kwargs):
        super().__init__(name="FoxNews",
                         base_url="https://www.foxnews.com/world",
                         xpath_list=["//main[@class='main-content']//h2[@class='title']//a",
                                     "//main[@class='main-content']//h4[@class='title']//a"],
                         **kwargs)


class TheGuardianSpider(XPathSpider):
    """Scraps The Guardian website"""

    def __init__(self, **kwargs):
        super().__init__(name="TheGuardian",
                         base_url="https://www.theguardian.com/international",
                         xpath_list=["(//a[@class='u-faux-block-link"
                                     "__overlay js-headline-text'])"],
                         **kwargs)


process = CrawlerProcess()
process.crawl(AlJazeeraSpider)
process.crawl(CnnSpider)
process.crawl(DWSpider)
process.crawl(FoxNewsSpider)
process.crawl(TheGuardianSpider)
process.start()
