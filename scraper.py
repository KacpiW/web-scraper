# %%
import time
import scrapy
import logging
import pandas as pd
import scrapy.crawler as crawler
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup


class OtoMotoScraper(scrapy.Spider):
    name = "otomotospider"

    custom_settings = {
        'DOWNLOAD_DELAY': '1.0',
        'AUTOTHROTTLE_ENABLED': True,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        }
    }

    offers_details = []

    def start_requests(self):
        urls = [
            'https://www.otomoto.pl/osobowe/',
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
            if 'carsmile' in item_url:
                continue
            else:
                yield scrapy.Request(url=item_url, callback=self.parse_offer_details)

        next_page = response.xpath(
            '//*[@id="body-container"]/div[2]/div[2]/ul/li[7]/a/@href').get()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_offer_details(self, response):
        self.logger.info(
            'Got successfull response from {html}'.format(html=response.url))

        details_dict = {}

        soup = BeautifulSoup(response.body, 'lxml')

        details = soup.find_all('li', attrs={'class': 'offer-params__item'})

        for index, detail in enumerate(details):
            if detail.find('a', attrs={'offer-params__link'}):
                key = detail.find('span', attrs={'offer-params__label'}).text
                value = detail.find('a', attrs={'offer-params__link'}).text

                if isinstance(key, str) & isinstance(value, str):
                    details_dict[key.strip()] = value.strip()

            else:
                key = detail.find('span', attrs={'offer-params__label'}).text
                value = detail.find('div', attrs={'offer-params__value'}).text

                if isinstance(key, str) & isinstance(value, str):
                    details_dict[key.strip()] = value.strip()

        details_dict['cena'] = soup.find(
            'span', attrs={'class': 'offer-price__number'}).text.strip()
        details_dict['lokalizacja'] = soup.find(
            'span', attrs={'class': 'seller-box__seller-address__label'}).text.strip()

        features = soup.find_all('li', attrs={'class': 'offer-features__item'})

        details_dict['wyposazenie'] = [feature.text.strip()
                                       for feature in features]

        self.offers_details.append(details_dict)


# %%
if __name__ == '__main__':
    process = CrawlerProcess({'LOG_LEVEL': 'INFO'})
    process.crawl(OtoMotoScraper)
    spider = next(iter(process.crawlers)).spider
    process.start()

    offers = spider.offers_details

# %%
