# %%
import time
import pandas as pd
import scrapy
import scrapy.crawler as crawler
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

url = 'https://www.otomoto.pl/osobowe/'


class OtoMotoScraper(scrapy.Spider):
    name = "otomotospider"

    custom_settings = {
        'DOWNLOAD_DELAY': '1.0',
        'AUTOTHROTTLE_ENABLED': True,
        'USER_AGENT': 'Peter Parker (peter.parker@myemail.com)'
    }

    def start_requests(self):
        urls = [
            'https://www.otomoto.pl/osobowe/?search%5Border%5D=created_at%3Adesc&page=1',
            'https://www.otomoto.pl/osobowe/?search%5Border%5D=created_at%3Adesc&page=2',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.logger.info(
            'Got successful response from {}'.format(response.url))

        soup = BeautifulSoup(response.body, 'lxml')

        offers = soup.find('div', attrs={'class': 'offers list'})

        offer_links = [link.get('href') for link in offers.find_all(
            'a', attrs={'class': 'offer-title__link'})]

        for item_url in offer_links:
            yield scrapy.Request(url=item_url, callback=self.parse_info)

    def parse_info(self, response):
        self.logger.info(
            'Got successfull response from {html}'.format(html=response.url))


# %%
if __name__ == '__main__':
    process = CrawlerProcess({'LOG_LEVEL': 'INFO'})
    process.crawl(OtoMotoScraper)
    process.start()

# %%
