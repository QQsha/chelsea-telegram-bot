import requests

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

def percentage(part, whole):
  return 100 * float(part)/float(whole)

def same_text(text, text2):
    text_list2 = text2.split(' ')
    length = len(text_list2)
    for li in text: 
        res = []
        for i in text_list2:
            if i in li:
                res.append(1)
            else:
                res.append(0) 
        sum_text = sum(res)
        perc = percentage(sum_text, length)
        if perc > 75:
            return False
    return True


