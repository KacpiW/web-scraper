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
        'USER_AGENT': 'Peter Parkson (peter.parker@myemail.com)'
    }

    offers_details = []

    def start_requests(self):
        urls = [
            'https://www.otomoto.pl/osobowe/?search%5Border%5D=created_at%3Adesc&page=1',
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

        i = 0
        for item_url in offer_links:
            yield scrapy.Request(url=item_url, callback=self.parse_offer_details)
            if i == 2:
                break
            i += 1

    def parse_offer_details(self, response):
        self.logger.info(
            'Got successfull response from {html}'.format(html=response.url))

        details_dict = {}

        soup = BeautifulSoup(response.body, 'lxml')

        details = soup.find('div', attrs={'class': 'offer-params with-vin'})\
            .find_all('li', attrs={'class': 'offer-params__item'})

        for index, detail in enumerate(details):
            try:
                key = detail.find('span', attrs={'offer-params__label'}).text
                value = detail.find('a', attrs={'offer-params__link'}).text

                if isinstance(key, str) & isinstance(value, str):
                    details_dict[key.strip()] = value.strip()

            except Exception as e:
                self.logger.info(e)

            details_dict['cena'] = soup.find(
                'span', attrs={'class': 'offer-price__number'}).text.strip()
            details_dict['lokalizacja'] = soup.find(
                'span', attrs={'class': 'seller-box__seller-address__label'}).text.strip()
            details_dict['wyposazenie'] = [feature for feature in soup.]

        self.offers_details.append(details_dict)


# %%
if __name__ == '__main__':
    process = CrawlerProcess({'LOG_LEVEL': 'INFO'})
    process.crawl(OtoMotoScraper)
    spider = next(iter(process.crawlers)).spider
    process.start()

    offers = spider.offers_details

# %%
