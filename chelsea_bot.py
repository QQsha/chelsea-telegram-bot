import sqlite3
import urllib
import time
from datetime import datetime
import re
import pytz
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
    header = re.findall(PATTERN_TITLE, html)
    news['caption'] = header[0]
    return news

def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={} \
    &caption={}&parse_mode=Markdown&disable_notification=True".format(
        chat_id, photo_link, caption)
    get_url(url)

def caption_filter(caption):
    raw_lst = [
        '.*(LIVE|Live)',
        '.*(odds and stats)',
        '.*(betting guide)',
        '.*(Premier League clubs)'
        ]
    regexes = []
    for raw_regex in raw_lst:
        regexes.append(re.compile(raw_regex))
    if any(regex.match(caption) for regex in regexes):
        return False
    return True

def scrapper(last_link):
    last_news_info = get_content(last_link)
    return last_news_info['caption'], last_news_info['image']

def percentage(part, whole):
    return 100 * (float(part)/float(whole))

def same_text(caption_store, caption):
    text_list = caption.split(' ')
    length = len(text_list)
    for cap in caption_store:
        res = []
        for i in text_list:
            if i in cap.split(' '):
                res.append(1)
            else:
                res.append(0)
        sum_text = sum(res)
        perc = percentage(sum_text, length)
        if perc > 69:
            return False
    return True

def db_con():
    dbase = sqlite3.connect('data/mydb', timeout=10)
    cursor = dbase.cursor()
    cursor.execute('''SELECT id, caption, link
                  FROM posts 
                  ORDER BY id DESC
                  LIMIT 10;''')
    all_rows = cursor.fetchall()
    dbase.close()
    return all_rows

def local_store(db_store):
    link_store = [link[2] for link in db_store]
    caption_store = [cap[1] for cap in db_store]
    print(link_store)
    return caption_store, link_store

def db_insert(caption, link):
    dbase = sqlite3.connect('data/mydb', timeout=10)
    cursor = dbase.cursor()
    cursor.execute('''INSERT INTO posts(caption, link) VALUES(:caption, :link)''',
                   {'caption':caption, 'link':link})
    dbase.commit()
    dbase.close()

def publish_post(last_caption, last_image, last_link, chat_id):
    message_text = "@Chelsea *NEWS:* \n" + last_caption + "."
    send_photo(chat_id, last_image, message_text)
    db_insert(last_caption, last_link)


def main():
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime(2018, 5, 22, 15, 58, 18, tzinfo=europe_timezone)
    while True:
        print("new pivot", datetime.now())
        news_url = parsing_news()
        last_link = news_url['link']
        if news_url['date'] > date_baseline:
            if re.match(r'.*/sport/.*', last_link):
                last_caption, last_image = scrapper(last_link)
                if caption_filter(last_caption):
                    db_store = db_con()
                    caption_store, link_store = local_store(db_store)
                    if last_link not in link_store:
                        if same_text(caption_store, last_caption):
                            publish_post(last_caption, last_image, last_link, CHAT_ID)
                            date_baseline = news_url['date']
                        else:
                            message_text = "@Chelsea _test:_ \n" + last_caption + "."
                            send_photo(CHAT_ID_TEST, last_image, message_text)
                            date_baseline = news_url['date']

        time.sleep(40)


if __name__ == '__main__':
    main()
