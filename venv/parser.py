import requests
from bs4 import BeautifulSoup
import  csv
import os

URL = 'https://www.citilink.ru/catalog/mobile/notebooks/?available=1&status=55395790&f=8392_3Endless,8392_3Freed1DOS,8392_3Freed1DOSd12b70,8392_3Freed1DOSd13b70,8392_3Linux,8392_3Linuxd1Ubuntu,8392_3Windowsd110d1triald1b3dlyad1oznakomleniyab4d1Home,12461_3nVidiad1GeForced1d1GTXd11650d1a5d14096d1mb,8392_3noOS,10659_315b76d1a3,277_3Cored1i5'
#URL = 'https://www.citilink.ru/catalog/mobile/notebooks/'
PARAMS = {}
#PARAMS = {'available': '1', 'status': '55395790', 'f': '8392_3Endless,8392_3Freed1DOS,8392_3Freed1DOSd12b70,8392_3Freed1DOSd13b70,8392_3Linux,8392_3Linuxd1Ubuntu,8392_3Windowsd110d1triald1b3dlyad1oznakomleniyab4d1Home,12461_3nVidiad1GeForced1d1GTXd11650d1a5d14096d1mb,8392_3noOS'}
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Geco/20100101 Firefox/71.0', 'accept':'*/*'}
PATH = 'notebooks.csv'

def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    page_listing = soup.find('div', class_ = 'page_listing')
    if (page_listing):
        pages = page_listing.find_all('li', class_ = 'next')
        if (pages):
            return int(pages[-1].get_text())
        else:
            return 1
    else:
        return 1

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_ = 'js--subcategory-product-item subcategory-product-item product_data__gtm-js product_data__pageevents-js ddl_product' )

    notebooks = []
    params = []
    for item in items:
        params_text = item.get('data-params').split(',"')
        price = params_text[2].split(':')
        fakeOldPrice = params_text[3].split(':')
        shortName = params_text[4].split(':')
        clubPrice = params_text[7].split(':')

        notebooks.append({
            #'title': item.find('a', class_= 'link_gtm-js link_pageevents-js ddl_product_link').get('title'),
            'title': shortName[1],
            'link': item.find('a', class_='link_gtm-js link_pageevents-js ddl_product_link').get('href'),
            'price': price[1],
            'fakeOldPrice': fakeOldPrice[1],
            'clubPrice': clubPrice[1],
        })
    return notebooks

def save_file(items, path):
    with open(path, 'w', newline = '') as file:
        writer = csv.writer(file, delimiter = ';')
        writer.writerow(['Название', 'Ссылка', 'Цена', 'Фейковая цена', 'Клубная цена'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['price'], item['fakeOldPrice'], item['clubPrice']])

def parse():
    html = get_html(URL, PARAMS)
    if html.status_code == 200:
        notebooks = []
        pages_count = get_pages_count(html.text)

        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}')
            PARAMS['p'] = page
            html = get_html(URL, PARAMS)
            notebooks.extend(get_content(html.text))
        save_file(notebooks, PATH)
        print (f'Получено ноутбуков {len(notebooks)}')
        os.startfile(PATH)
    else:
        print('Error')

parse()