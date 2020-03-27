import scrapy

class CnnScrapy(scrapy.Spider):
    name = 'CNN'

    baseUrl = 'https://www.cnn.com/world'

    start_urls = [
       baseUrl
    ]

    def parse(self, response):
        for title in response.xpath("(//section[@class='zn zn-world-zone-1 zn-left-fluid-right-stack zn--idx-0 zn--ordinary t-light zn-has-two-containers' or @class='zn zn-world-zone-2 zn-balanced zn--idx-1 zn--ordinary t-light zn-has-multiple-containers zn-has-6-containers']//h3[@class='cd__headline']//a)"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.cnn.com/world' + str(absoluteUrl)
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absoluteUrl
            }
