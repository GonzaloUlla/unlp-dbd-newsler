import scrapy


class FoxNewsScrapy(scrapy.Spider):
    name = 'FoxNews'

    base_url = 'https://www.foxnews.com/world'

    start_urls = [
        base_url
    ]

    def parse(self, response):
        for title in response.xpath("//main[@class='main-content']//h2[@class='title']//a"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.foxnews.com/world' + absolute_url
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absolute_url
            }
        # Could not use a single xPath for these secondary headers
        for title in response.xpath("//main[@class='main-content']//h4[@class='title']//a"):
            absolute_url = title.xpath("@href").get()
            if "https" not in absolute_url:
                absolute_url = 'https://www.foxnews.com/world' + absolute_url
            yield {
                'news_text': title.xpath(".//text()").get(),
                'news_href': absolute_url
            }
