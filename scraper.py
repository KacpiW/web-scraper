# %%
from bs4.element import SoupStrainer
import requests
from bs4 import BeautifulSoup

url = 'https://www.otomoto.pl/osobowe/'


def get_sales_offers(url):
    req = requests.get(url)

    soup = BeautifulSoup(req.text, 'lxml')

    offers_list = soup.find(
        'div', attrs={'class': 'offers list'}).find_all('article')

    for offer in offers_list:
        print(offer['data-param-make'])


if __name__ == '__main__':
    get_sales_offers(url=url)

# %%

# %%
