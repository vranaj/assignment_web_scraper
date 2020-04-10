import requests
from bs4 import BeautifulSoup
import datetime as dt
import timestring
import re
import json

url_prefix = "https://ikman.lk"
url_suffix = '/en/ads?by_paying_member=0&sort=relevance&buy_now=0&query=bmw&page=1'
dom_element = requests.get(url_prefix + url_suffix).text
soup_content = BeautifulSoup(dom_element, 'html.parser')

top_ads = soup_content.find_all('li', {"class": 'gtm-top-ad'})
normal_ads = soup_content.find_all('li', {"class": 'gtm-normal-ad'})

i = 0
webScraperDict = {}

def getImages(url):
    _dom_element = requests.get(url_prefix + url).text
    _soup_content = BeautifulSoup(_dom_element, 'html.parser')
    _images = _soup_content.find('div', {"class": "gallery-item"})
    if(_images == None):
        return getImages(url)
    else:
        imageListString = _images.find('img')
        imageList = imageListString['data-srcset'].split(',')
        newImageList = []

        for imageUrl in imageList:
            newImageList.append(imageUrl.split('jpg')[0]+'jpg')

        return newImageList

def getDescription(url):
    _dom_element = requests.get(url_prefix + url).text
    _soup_content = BeautifulSoup(_dom_element, 'html.parser')
    _description = _soup_content.findAll('div', {"class": "description--1nRbz"})

    _fullDescription = ''
    if (_description == []):
        return getDescription(url)
    else:
        for div in _description:
            tempDescList = div.findAll('p')
            _fullDescription = ', '.join(map(str, tempDescList))
            _fullDescription = _fullDescription.replace('<p>', '').replace('</p>', ', ').replace(',', '')

        return _fullDescription

def getData(url):
    _dom_element = requests.get(url_prefix + url).text
    _soup_content = BeautifulSoup(_dom_element, 'html.parser')
    _title = _soup_content.find('h1', {"class": "title--3s1R8"})
    _time = _soup_content.find('h3', {"class": "sub-title--37mkY"})
    _price = _soup_content.find('div', {"class": "amount--3NTpl"})
    _contacts = _soup_content.find('div', {"class": "icons--1iEHU"})
    _category = _soup_content.findAll('div', {"class": "ellipsis--1NS5-"})

    if(_title == None or _time == None or _price == None or _contacts == None or _category == []):
        return getData(url)

    else:
        _title = _title.text
        _price = _price.text

        _time = _time.text.replace('Posted on ', '').split(',')
        if(_time[0]):
            _time = timestring.Date(_time[0]).date.strftime('%Y-%m-%d')

        _contacts = _contacts.a['href']

        _new_category = _category[len(_category) - 2]

        return {
            'title': _title,
            'date': _time,
            'price': _price,
            'contact': _contacts.split(':')[1],
            'category': _new_category.text
        }

for div in normal_ads:

    commonData = getData(div.a['href'])
    description = getDescription(div.a['href'])
    images = getImages(div.a['href'])

    tempArray = {
        'title': commonData['title'],
        'date': commonData['date'],
        'category': commonData['category'],
        'url': div.a['href'],
        'details': {
          'full_description': description,
          'image_urls': images,
          'price': commonData['price'],
          'contact': commonData['contact']
        }
    }

    print(tempArray)
    with open('data.json') as json_file:
        webScraperDict = json.load(json_file)

    with open('data.json', 'w') as outfile:
        webScraperDict[i] = tempArray
        json.dump(webScraperDict, outfile)


    i=i+1



