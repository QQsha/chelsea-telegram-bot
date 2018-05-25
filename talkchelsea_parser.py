import requests
import re
import html

from bs4 import BeautifulSoup

''' parsing news '''
URL = "https://www.talkchelsea.net/feed/"
resp = requests.get(URL)
PATTERN_IMAGE = r'.*src="(.*)" class'
PATTERN_DESC = r'/>(.*\.) '
soup = BeautifulSoup(resp.content, features='xml')
items = soup.findAll('item')
info_news = []


def parsing_news():
    for item in items:
        news = dict()
        news['title'] = item.title.text
        news['date'] = item.pubDate.text
        news['image'] = re.findall(PATTERN_IMAGE, item.description.text)[0]
        encoded_html = re.findall(PATTERN_DESC, item.description.text)[0]
        news['description'] = html.unescape(encoded_html)
        info_news.append(news)
    return info_news[0]
