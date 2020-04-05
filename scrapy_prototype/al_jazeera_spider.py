import scrapy


class AlJazeeraScrapy(scrapy.Spider):
    name = 'AlJazeera'

    baseUrl = 'https://www.aljazeera.com'

    start_urls = [
        baseUrl + '/news'
    ]

    def parse(self, response):
        for title in response.xpath(
                "//a//h2[@class='top-sec-title' or @class='top-sec-smalltitle' or "
                "@class='topics-sec-item-head']/parent::a"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.aljazeera.com' + absolute_url
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absolute_url
            }
