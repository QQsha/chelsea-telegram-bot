import os
import re
import time
import urllib
from datetime import datetime

import psycopg2
import pytz
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

TOKEN = os.environ.get('BOT_TOKEN')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CHAT_ID = "@Chelsea"
CHAT_ID_TEST = "-1001279121498"

PATTERN_IMAGE = r'og:image" content="(.*)"'
PATTERN_TITLE = r'.*<h2>(.*)</h2>'

# parsing dailymail rss feed
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

# get request
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# telgram post method
def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={} \
    &caption={}&parse_mode=Markdown&disable_notification=True".format(
        chat_id, photo_link, caption)
    get_url(url)

# caption filter
def caption_filter(caption):
    raw_lst = [
        '.*(RSS)',
        '.*(LIVE|Live)',
        '.*(odds|stats)',
        '.*(betting guide)',
        '.*(Premier League)',
        '.*(THINGS|things)',
        '.*(RESULT)'
    ]
    regexes = []
    for raw_regex in raw_lst:
        regexes.append(re.compile(raw_regex))
    if any(regex.match(caption) for regex in regexes):
        return False
    return True

# return caption text, and image link
def scrapper(url):
    news = {}
    html = get_url(url)
    news['image'] = re.findall(PATTERN_IMAGE, html)[0]
    header = re.findall(PATTERN_TITLE, html)
    news['caption'] = header[0]
    return news['caption'], news['image']

# return % part number of whole number
def percentage(part, whole):
    return 100 * (float(part)/float(whole))

# function for checking double posting
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

# Postgres connect
def con_postgres():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url, sslmode='require')
    cursor = conn.cursor()
    return conn, cursor

# returning 10 last posts from db
def db_con():
    conn, cursor = con_postgres()
    cursor.execute('''SELECT id, caption, link
                  FROM posts 
                  ORDER BY id DESC
                  LIMIT 10;''')
    all_rows = cursor.fetchall()
    conn.close()
    return all_rows

# getting caption and link from posts
def local_store(db_store):
    link_store = [link[2] for link in db_store]
    caption_store = [cap[1] for cap in db_store]
    return caption_store, link_store

# adding new post in db
def db_insert(caption, link):
    conn, cursor = con_postgres()
    cursor.execute(
        "INSERT INTO posts (caption, link) VALUES (%s, %s)", (caption, link))
    conn.commit()
    conn.close()

# commit post in Telegram
def publish_post(last_caption, last_image, last_link, chat_id):
    message_text = "@Chelsea *NEWS:* \n" + last_caption + "."
    send_photo(chat_id, last_image, message_text)
    db_insert(last_caption, last_link)


def main():
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime.now(europe_timezone)
    while True:
        print("new pivot", datetime.now(europe_timezone))
        news_url = parsing_news()
        last_link = news_url['link']
        if (news_url['date'] > date_baseline) & bool(re.search(r'.*/sport/.*', last_link)):
            last_caption, last_image = scrapper(last_link)
            if caption_filter(last_caption):
                db_store = db_con()
                caption_store, link_store = local_store(db_store)
                if (last_link not in link_store) & (same_text(caption_store, last_caption)):
                    publish_post(last_caption, last_image, last_link, CHAT_ID)
                    date_baseline = news_url['date']
        time.sleep(40)


if __name__ == '__main__':
    main()
