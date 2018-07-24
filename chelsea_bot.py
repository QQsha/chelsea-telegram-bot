import urllib
import time
from datetime import datetime
import pytz
import re

import dailymail_rss_parser as drp
import dailymail_parser as dp

TOKEN = "569665229:AAFFOoITLtgjpxsWtAoHTATMNv5mex53JXU"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CHAT_ID = "-1001279121498"


def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown".format(chat_id, photo_link, caption)
    dp.get_url(url)


def main():
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime(2018, 5, 22, 15, 58, 18, tzinfo=europe_timezone)
    caption_store = []
    while True:
        print("new pivot", datetime.now())
        news_url = drp.parsing_news()
        print(news_url['date'], "Date of last post")
        if news_url['date'] > date_baseline:
            print('date is good')
            if re.match(r'.*/sport/.*', news_url['link']):
                print("link is sport")
                last_news_info = dp.get_content(news_url['link'])
                last_caption = last_news_info['caption']

                if not re.match(r'.*Transfer [n, N]ews (LIVE|RECAP):.*', last_caption):
                    if last_news_info['caption'] not in caption_store:
                        print("news is not transfer, posting news")
                        message_text = "_@Chelsea NEWS:_ \n" + "*" + last_caption + "." + "*"
                        send_photo(CHAT_ID, last_news_info['image'], message_text)
                        date_baseline = news_url['date']

                caption_store.append(last_caption)
                if len(caption_store) > 30:
                    caption_store.popleft()
        time.sleep(31)


if __name__ == '__main__':
    main()
