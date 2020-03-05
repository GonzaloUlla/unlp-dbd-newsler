import scrapy

class TheGuardianScrapy(scrapy.Spider):
    name = 'TheGuardian'

    start_urls = [
        'https://www.theguardian.com/international'
    ]

    def parse(self, response):
        for title in response.xpath("(//a[@class='u-faux-block-link__overlay js-headline-text'])"):
            #print(title.xpath(".//text()").get()+"\n")
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': title.xpath("@href").get()
            }


