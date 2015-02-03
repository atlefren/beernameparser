# -*- coding: utf-8 -*-

import math
import re
import urllib
import HTMLParser
import copy
import json
from datetime import datetime

import requests
from BeautifulSoup import BeautifulSoup

from base_write import write_vp_data


html_unescape = HTMLParser.HTMLParser().unescape


def get_products(soup):
    return soup.find('tbody').findAll('tr')


def get_facet(element, index):
    return element.findAll('span', {'class': 'facet'})[index].string.strip()


def find_between(str, start, end):
    result = re.search('%s(.*)%s' % (start, end), str)
    return result.group(1)


def get_data(element):
    if element:
        return html_unescape(
            element.find('span', {'class': 'data'}).string.strip()
        )
    return None


def parse_price(string):
    return float(
        string.
        replace(',', '.').
        replace('Kr. ', '').
        replace('-', '0').
        strip()
    )


def parse_abv(data):
    if data:
        string = get_facet(data, 0)
        return float(find_between(string, 'Alkohol ', '%').replace(',', '.'))
    return None


def parse_size(string):
    match = re.search('\((.*)&nbsp;cl\)', string)
    return float(match.group(1).replace(',', '.'))


def parse_product(row):

    link = row.find('a', {'class': 'product'})
    url = link.get('href').split(';pgid')[0]
    result = re.search('/sku-(.*)', url)
    id = int(result.group(1))

    info = row.find('td', {'class': 'price'})
    price = parse_price(info.find('strong').text)
    size = parse_size(info.find('em').text)

    stock = row.find('td', {'class': 'add'})\
        .find('h3', {'class': 'stock'})\
        .text.strip()

    return {
        'name': html_unescape(link.text),
        'url': url,
        'id': id,
        'price': price,
        'size': size,
        'stock': html_unescape(stock)
    }


def get_store_id(url):
    match = re.search('butikk_id=([0-9]*)', url)
    return int(match.group(1))


def parse_stock_and_date(info):
    match = re.search('^\(([0-9]*) p&aring; lager\)Oppdatert (.*)', info)
    if match:
        return int(match.group(1)), match.group(2)
    return (None, None)


def parse_store(soup):

    link = soup.find('a')
    url = link.get('href')

    info = soup.find('em').text
    stock, date = parse_stock_and_date(info)
    id = get_store_id(url)
    date_str = None
    if date:
        date_str = datetime.strptime(date, '%d.%m.%Y %H:%M:%S').isoformat()
    return {
        'id': id,
        'stock': stock,
        'date': date_str,
    }


def find_attrib(list, attrib):
    for li in list:
        el = li.find('strong', {'class': 'attrib'})
        if el.text.replace(':', '') == attrib:
            return li
    return None


def parse_js_coord(line):
        match = re.search("([0-9]*\.[0-9]*)", line)
        return float(match.group(1))


def cleanup_brewery(name):
    cleanups = {
        'Lervig Aktiebrygeri': 'Lervig Aktiebryggeri',
        'Achel Brewery': 'Brouwerij der Trappistenabdij De Achelse Kluis',
        'Baladin': 'Le Baladin',
        'B.O.M Brewery': 'BOMBrewery (Belgian Original Maltbakery)',
        'Adnams Sole Bay Brewery': 'Adnams',
        'LWC Drinks': 'Hepworth',
        'Egersund Mineralvandfabrik': 'Berentsens Brygghus',
        'Berentsens': 'Berentsens Brygghus',
        'Brasserie BFM SA': 'BFM (Brasserie des Franches-Montagnes)',
        'Crafty Dan Micro Brewery/Thwai': 'Thwaites',
        'Bitburger Brauerei': 'Bitburger Brauerei Th. Simon',
        'Vifilfell': u'Viking Ölgerd',
        'Browerij Bockor': 'Brouwerij Omer Vander Ghinste',
        'Brew Dog': 'Brewdog Brewery',
        'Grolsch Bierbrouwerij Int.': 'Grolsche Bierbrouwerij Ned.',
        u'Macks Ølbryggeri AS': 'Mack Bryggeri',
        u'Mack\'s Ølbryggeri og Mineralva': 'Mack Bryggeri',
        'Sundbytunet Bryggeri og Destil': 'Sundbytunet',
        'Brasserie St. Feuillien': 'Brasserie St-Feuillien / Friart',
        'Mikkeller\De Proef Brouwerij': 'Mikkeller',
        'Meinklang': 'Brauerei Gusswerk',
        'Borg Bryggerier': 'Hansa Borg Bryggerier',
        u'Tucher Braü': 'Tucher Bräu Fürth',
        u'Tucker Bräu': 'Tucher Bräu Fürth',
        'Brasserie Artesienne': u'Brasserie Artésienne',
        'NiuBru S.R.L. - Brewfist': 'Brewfist',
        'Brutal Brewing': 'Spendrups Bryggeri',
        u'Hofbräu': u'Staatliches Hofbräuhaus München',
        'Anheuser-Busch': 'Anheuser-Busch InBev',
        'Ugly Duck Brewing Co.': 'Indslev Bryggeri',
        'Bodejovice Budvar': 'Budweiser Budvar Ceske Budejovice',
        'Cold Boy': 'ColdBoy Brewery',
        u'Einstök Brewery': 'Einstök Ölgerð',
        'Weihenstephan Bayerische Staat': 'Bayerische Staatsbrauerei Weihenstephan',
        u'Nøgne Ø Det kompromissløse Bry': u'Nøge Ø'
    }
    if name in cleanups:
        return cleanups[name]
    return name

class Beer(object):

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.url = kwargs['url']
        self.id = kwargs['id']
        self.price = kwargs['price']
        self.size = kwargs['size']
        self.stock = kwargs['stock']
        self.brewery = None
        self.stores = None

    def display(self):
        if self.brewery:
            return '%s - %s (%s)' % (self.brewery, self.name, self.abv)
        else:
            return self.name

    def get_details(self):
        params = {
            'HideDropdownIfNotInStock': 'true',
            'ShowShopsWithProdInStock': 'true',
        }
        url = self.url + '?' + urllib.urlencode(params)
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text)
        product_data = soup.find('div', {'class': 'productData'})

        data = product_data.findAll('li')
        self.brewery = cleanup_brewery(
            get_data(find_attrib(data, 'Produsent'))
        )

        self.type = get_data(find_attrib(data, 'Varetype'))
        self.pol_type = get_data(find_attrib(data, 'Produktutvalg'))
        self.pol_cat = get_data(find_attrib(data, 'Butikkategori'))
        self.country = get_data(find_attrib(data, 'Land/distrikt'))
        self.abv = parse_abv(find_attrib(data, 'Innhold'))

        self.stores = self.get_stores(soup)

    def get_stores(self, soup):
        stores = []
        list = soup.find('div', {'class': 'listStores'})
        if list:
            for store in list.findAll('li'):
                stores.append(parse_store(store))
        return stores

    def get_stock(self):

        num = sum([store['stock'] for store in self.stores])
        return '%s bottles in %s stores' % (num, len(self.stores))


class BeerParser(object):

    def __init__(self):
        self.list_url = 'http://www.vinmonopolet.no/vareutvalg/sok?'

        self.search_params = {
            'query': '*',
            'sort': '2',
            'sortMode': '0',
            'filterIds': '25',
            'filterValues': 'Øl',
        }

    def get_soup_for_page(self, page):
        params = copy.copy(self.search_params)
        params['page'] = page
        url = self.list_url + urllib.urlencode(params)
        response = requests.get(url)
        if response.status_code != 200:
            None
        return BeautifulSoup(response.text)

    def get_beer_list(self):

        soup = self.get_soup_for_page(1)
        beers = self.get_beers(soup)

        for page in range(2, self.get_num_pages(soup) + 1):
            beers += self.get_beers(self.get_soup_for_page(page))

        beer_list = []
        for beer in beers:
            beer.get_details()
            beer_list.append(beer.__dict__)

        return beer_list

    def get_num_pages(self, soup):
        num = soup.find('span', {'class': 'count'}).text
        return int(math.ceil(int(num) / 30.0))

    def get_beers(self, soup):
        return [Beer(**parse_product(product))
                for product in get_products(soup)]

    def parse_pol_page(self, html):
        soup = BeautifulSoup(html)
        list = soup.find('div', {'id': 'storeInfo'})
        pol = []
        for store in list.findAll('li'):
            link = store.find('a')
            id = get_store_id(link.get('href'))
            name = html_unescape(link.text.strip())
            pol.append({'id': id, 'name': name})

        map_js = soup.findAll(
            'div',
            {'class': 'content'}
        )[1].findAll('script')[1].text

        latitudes = []
        longitudes = []
        for line in map_js.split('\n'):
            line = line.strip()
            if line.startswith('var shopCoordN = '):
                latitudes.append(parse_js_coord(line))
            if line.startswith('var shopCoordE = '):
                longitudes.append(parse_js_coord(line))

        for index, (lat, lon) in enumerate(zip(latitudes, longitudes)):
            pol[index]['lat'] = lat
            pol[index]['lon'] = lon
        return pol

    def get_pol_list(self):
        base_url = 'http://www.vinmonopolet.no/butikker?fylke_id='

        pol = []
        for i in range(1, 20):
            id = '{0:02d}'.format(i)
            pol += self.parse_pol_page(requests.get(base_url + id).text)
        return pol

if __name__ == '__main__':

    parser = BeerParser()

    #pol = parser.get_pol_list()
    #with open('pol.json', 'w') as pol_file:
    #    pol_file.write(json.dumps(pol))

    #beers = parser.get_beer_list()
    #with open('beers.json', 'w') as beer_file:
    #    beer_file.write(json.dumps(beers, indent=4))

    with open('beers_cleaned.json', 'r') as json_file:
        data = json.loads(json_file.read())
        write_vp_data(data)
