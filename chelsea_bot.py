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

def percentage(part, whole):
    return 100 * (float(part)/float(whole))

def same_text(caption_store, caption):
    text_list = caption.split(' ')
    length = len(text_list)
    for li in caption_store: 
        res = []
        for i in text_list:
            if i in li:
                res.append(1)
            else:
                res.append(0) 
        sum_text = sum(res)
        perc = percentage(sum_text, length)
        if perc > 69:
            return False
    else:
        return True
    

def main():
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime(2018, 5, 22, 15, 58, 18, tzinfo=europe_timezone)
    link_store = []
    caption_store = []
    while True:
        print("new pivot", datetime.now())
        news_url = parsing_news()
        last_link = news_url['link']
        if news_url['date'] > date_baseline:
            if re.match(r'.*/sport/.*', last_link):
                last_news_info = get_content(last_link)
                last_caption = last_news_info['caption']
                last_image = last_news_info['image']

                if caption_filter(last_caption):
                    if last_link not in link_store:
                        if same_text(caption_store, last_caption):
                            message_text = "@Chelsea *NEWS:* \n" + last_caption + "."
                            send_photo(CHAT_ID, last_image, message_text)
                            date_baseline = news_url['date']

                            link_store.append(last_link)
                            if len(link_store) > 30:
                                link_store.pop(0)
                            
                            lc_list = last_caption.split(' ')
                            caption_store.append(lc_list)
                            if len(caption_store) > 30:
                                caption_store.pop(0)

                        else:
                            message_text = "@Chelsea _test:_ \n" + last_caption + "."
                            send_photo(CHAT_ID_TEST, last_image, message_text)
                            date_baseline = news_url['date']

        time.sleep(40)


if __name__ == '__main__':
    main()
