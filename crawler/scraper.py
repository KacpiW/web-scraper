import os
import json
import scrapy
import datetime
import scrapy.crawler as crawler
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

if __package__ is None or __package__ == "":
    from logger import logger
else:
    from .logger import logger


class OtoMotoScraper(scrapy.Spider):
    """A class to download data from Otomoto passanger car offers website.

        Provides methods to iterate over all subpages containing passanger
        cars offers, as well as method to retrive all possible data provided by sellers,
        thus parsed results may differ in number of acttributes in case some seller provided all
        possible information about the car or not. Class saves all downloaded information
        to json file line by line so there was no problem with RAM memmory usage.

    """

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
        """Request generator to request all website pages with passanger car offers.

        Yields:
            [generator object]: Generator object containing http request results
                 that is called on parse method
        """
        urls = [
            "https://www.otomoto.pl/osobowe/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parsing provided webiste and collecting all links to existing car offers
        excluding 'carsmile' advertisements and calling function to retrive all possible
        data regarding a car.


        Args:
            response (scrapy.Request()): scrapy.Request() website object

        Yields:
            [generator object]: Generator object conatining http request results
                that is called on pase_offer_details method 
        """

        logger.info(
            "Got successful response from {}".format(response.url))

        soup = BeautifulSoup(response.body, "lxml")

        offers = soup.find("div", attrs={"class": "offers list"})

        # Getting all offer links found on a page
        offer_links = [link.get("href") for link in offers.find_all(
            "a", attrs={"class": "offer-title__link"})]

        # Iterating over offers found on a page
        for item_url in offer_links:
            if "carsmile" in item_url:
                logger.warning(
                    "A website with carsmile string has been skipped.")
                continue
            else:
                yield scrapy.Request(url=item_url, callback=self.parse_offer_details)

        # Clicking next page button if there is any
        next_page = response.xpath(
            '//*[@id="body-container"]/div[2]/div[2]/ul/li[7]/a/@href').get()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_offer_details(self, response):
        """ Parsing website and collecting all details regarding a car provided
            in response argument. 

        Args:
            response ([http request]): scrapy.Request() website object 
        """
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

            # Number of 'Wyposazenie' items varies heavily, thus we download all
            # to one list and keep it as a backup information
            features = soup.find_all(
                "li", attrs={"class": "offer-features__item"})

            details_dict["wyposazenie"] = [feature.text.strip()
                                           for feature in features]

            self.save_to_file(details_dict)
            logger.info("All car offer details downloaded correctly.")

        except Exception as e:
            logger.warning("Failed to parse car offer details.")

    def save_to_file(self, to_save):
        """Saving car details to a json file.

        Args:
            to_save (dict): Dictionary containing all collected information
                regarding a car 
        """

        # Setting path by going to current folder parent directory
        # and set it to results/ directory
        save_path = os.path.abspath(os.path.join(os.path.dirname(
            __file__), os.pardir, 'results/otomoto_passanger_car_data_'))
        file_path = save_path + \
            str(datetime.date.today().strftime("%d_%m_%Y")) + ".json"

        if os.path.isfile(file_path):
            with open(file_path, mode="a") as out_file:
                json.dump(to_save, out_file)
                out_file.write("\n")
                logger.info(
                    "Appended new data to already existing json file.")

        else:
            with open(file_path, mode="w") as out_file:
                json.dump(to_save, out_file)
                out_file.write("\n")
                logger.info(
                    "Created and added first line of a data to json file.")


if __name__ == "__main__":
    process = CrawlerProcess({"LOG_LEVEL": "INFO"})
    process.crawl(OtoMotoScraper)
    spider = next(iter(process.crawlers)).spider
    process.start()
