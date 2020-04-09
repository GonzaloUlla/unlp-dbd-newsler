import scrapy

class FoxNewsScrapy(scrapy.Spider):
    name = 'FoxNews'

    baseUrl = 'https://www.foxnews.com/world'
    start_urls = [
        baseUrl
    ]

    def parse(self, response):
        for title in response.xpath("//main[@class='main-content']//h2[@class='title']//a"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.foxnews.com/world' + absoluteUrl
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absoluteUrl
            }
        # Could not use a single xPath for these secondary headers
        for title in response.xpath("//main[@class='main-content']//h4[@class='title']//a"):
            absoluteUrl = title.xpath("@href").get()
            if "https" not in absoluteUrl:
                absoluteUrl = 'https://www.foxnews.com/world' + absoluteUrl
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absoluteUrl
            }
