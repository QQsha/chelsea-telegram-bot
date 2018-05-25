import requests
import lxml

from bs4 import BeautifulSoup
from dateutil.parser import parse


def parsing_news():
    url = "http://www.dailymail.co.uk/sport/teampages/chelsea.rss"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, 'xml')
    items = soup.findAll('item')
    info_news = []
    for item in items:
        news = dict()
        news['link'] = item.link.text.strip()
        news['date'] = parse(item.pubDate.text)
        info_news.append(news)
    return info_news[0]



