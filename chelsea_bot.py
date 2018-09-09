import urllib
import time
from datetime import datetime
import pytz
import re
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse


TOKEN = "569665229:AAFFOoITLtgjpxsWtAoHTATMNv5mex53JXU"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CHAT_ID = "@Chelsea"
CHAT_ID_TEST = "-1001279121498"

PATTERN_IMAGE = r'og:image" content="(.*)"'
PATTERN_TITLE = r'.*<h2>(.*)</h2>'


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

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_content(url):
    news = {}
    html = get_url(url)
    news['image'] = re.findall(PATTERN_IMAGE, html)[0]
    h2 = re.findall(PATTERN_TITLE, html)
    news['caption'] = h2[0]
    return news


def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown&disable_notification=True".format(chat_id, photo_link, caption)
    get_url(url)

def date_checker(date):
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime(2018, 5, 22, 15, 58, 18, tzinfo=europe_timezone)
    if date > date_baseline:
        return True

def sport_checker(link):
    if re.match(r'.*/sport/.*', link):
        last_news_info = get_content(link)
        last_caption = last_news_info['caption']
        last_image = last_news_info['image']


def main():
    link_store = []
    while True:
        print("new pivot", datetime.now())
        news_url = parsing_news()
        last_link = news_url['link']
        if date_checker(news_url['date']):
            if re.match(r'.*/sport/.*', last_link):
                last_news_info = get_content(last_link)
                last_caption = last_news_info['caption']
                last_image = last_news_info['image']

            if not re.match(r'LIVE|Live', last_caption):
                if last_link not in link_store:
                    message_text = "@Chelsea *NEWS:* \n" + last_caption + "."
                    send_photo(CHAT_ID, last_image, message_text)
                    date_baseline = news_url['date']

                    link_store.append(last_link)
                    if len(link_store) > 30:
                        link_store.pop(0)

                else:
                    message_text = "@Chelsea _NEWS:_ \n" + last_caption + "."
                    send_photo(CHAT_ID_TEST, last_image, message_text)
                    date_baseline = news_url['date']

        time.sleep(40)


if __name__ == '__main__':
    main()
