import scrapy


class DeutscheWelle(scrapy.Spider):
    name = 'DW'

    base_url = 'https://www.dw.com/en/top-stories/world/s-1429'

    start_urls = [
        base_url
    ]

    def parse(self, response):
        for title in response.xpath("//a//h2[@class='linkable']/parent::a"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.dw.com/en/top-stories/world/s-1429' + absolute_url
            yield {
                'news_text': title.xpath(".//child::h2/text()").get().strip('\n'),
                'news_href': absolute_url
            }
        for title in response.xpath("//a//div[@class='teaserContentWrap']//h2/../parent::a"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.dw.com/en/top-stories/world/s-1429' + absolute_url
            yield {
                'news_text': title.xpath(".//child::h2/text()").get().strip('\n'),
                'news_href': absolute_url
            }
