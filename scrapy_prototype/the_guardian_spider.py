import scrapy

class TheGuardianScrapy(scrapy.Spider):
    name = 'TheGuardian'

    baseUrl = 'https://www.theguardian.com/international'

    start_urls = [
        baseUrl
    ]

    def parse(self, response):
        for title in response.xpath("(//a[@class='u-faux-block-link__overlay js-headline-text'])"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.theguardian.com/international' + absoluteUrl
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absoluteUrl
            }
