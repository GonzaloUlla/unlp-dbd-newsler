import scrapy


class TheGuardianScrapy(scrapy.Spider):
    name = 'TheGuardian'

    base_url = 'https://www.theguardian.com/international'

    start_urls = [
        base_url
    ]

    def parse(self, response):
        for title in response.xpath("(//a[@class='u-faux-block-link__overlay js-headline-text'])"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.theguardian.com/international' + absolute_url
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absolute_url
            }
