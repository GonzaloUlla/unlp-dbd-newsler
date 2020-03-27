import scrapy

class DeutscheWelle(scrapy.Spider):
    name = 'DW'

    baseUrl = 'https://www.dw.com/en/top-stories/world/s-1429'

    start_urls = [
        baseUrl
    ]

    def parse(self, response):
        for title in response.xpath("//a//h2[@class='linkable']/parent::a"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.dw.com/en/top-stories/world/s-1429'+absoluteUrl
            yield {
                'news_text': title.xpath(".//child::h2/text()").get().strip('\n'),
                'news_href': absoluteUrl
            }
        for title in response.xpath("//a//div[@class='teaserContentWrap']//h2/../parent::a"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.dw.com/en/top-stories/world/s-1429'+absoluteUrl
            yield {
                'news_text': title.xpath(".//child::h2/text()").get().strip('\n'),
                'news_href': absoluteUrl
            }