# %%
import logging
import os
import json
import scrapy
import datetime
import pandas as pd
import scrapy.crawler as crawler
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

if __package__ is None or __package__ == "":
    from logger import logger
else:
    from .logger import logger


class OtoMotoScraper(scrapy.Spider):
    name = "otomotospider"

    custom_settings = {
        "DOWNLOAD_DELAY": "1.0",
        "AUTOTHROTTLE_ENABLED": True,
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
        }
    }

    def start_requests(self):
        urls = [
            "https://www.otomoto.pl/osobowe/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logger.info(
            "Got successful response from {}".format(response.url))

        soup = BeautifulSoup(response.body, "lxml")

        offers = soup.find("div", attrs={"class": "offers list"})

        offer_links = [link.get("href") for link in offers.find_all(
            "a", attrs={"class": "offer-title__link"})]

        for item_url in offer_links:
            if "carsmile" in item_url:
                logger.warning(
                    "A website with carsmile string has been skipped.")
                continue
            else:
                yield scrapy.Request(url=item_url, callback=self.parse_offer_details)

        next_page = response.xpath(
            '//*[@id="body-container"]/div[2]/div[2]/ul/li[7]/a/@href').get()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_offer_details(self, response):
        logger.info(
            "Got successfull response from {html}".format(html=response.url))

        details_dict = {}

        soup = BeautifulSoup(response.body, "lxml")

        details = soup.find_all("li", attrs={"class": "offer-params__item"})

        try:
            for index, detail in enumerate(details):
                if detail.find("a", attrs={"offer-params__link"}):
                    key = detail.find(
                        "span", attrs={"offer-params__label"}).text
                    value = detail.find("a", attrs={"offer-params__link"}).text

                    if isinstance(key, str) & isinstance(value, str):
                        details_dict[key.strip()] = value.strip()

                else:
                    key = detail.find(
                        "span", attrs={"offer-params__label"}).text
                    value = detail.find(
                        "div", attrs={"offer-params__value"}).text

                    if isinstance(key, str) & isinstance(value, str):
                        details_dict[key.strip()] = value.strip()

            details_dict["cena"] = soup.find(
                "span", attrs={"class": "offer-price__number"}).text.strip()
            details_dict["lokalizacja"] = soup.find(
                "span", attrs={"class": "seller-box__seller-address__label"}).text.strip()

            features = soup.find_all(
                "li", attrs={"class": "offer-features__item"})

            details_dict["wyposazenie"] = [feature.text.strip()
                                           for feature in features]

            self.save_to_file(details_dict)
            logging.info("All car offer details downloaded correctly.")

        except Exception as e:
            logging.warning("Failed to parse car offer details.")

    def save_to_file(self, to_save):

        save_path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), os.pardir, 'results/otomoto_passanger_car_data_'))
        file_path = save_path + \
            str(datetime.date.today().strftime("%d_%m_%Y")) + ".json"

        if os.path.isfile(file_path):
            with open(file_path, mode="a") as out_file:
                json.dump(to_save, out_file)
                out_file.write("\n")
                logging.info(
                    "Appended new data to already existing json file.")

        else:
            with open(file_path, mode="w") as out_file:
                json.dump(to_save, out_file)
                out_file.write("\n")
                logging.info(
                    "Created and added first line of a data to json file.")


# %%
if __name__ == "__main__":
    process = CrawlerProcess({"LOG_LEVEL": "INFO"})
    process.crawl(OtoMotoScraper)
    spider = next(iter(process.crawlers)).spider
    process.start()

# %%
