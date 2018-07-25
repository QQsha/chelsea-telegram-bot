import urllib
import time
from datetime import datetime
import pytz
import re

import dailymail_rss_parser as drp
import dailymail_parser as dp

TOKEN = "569665229:AAFFOoITLtgjpxsWtAoHTATMNv5mex53JXU"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
CHAT_ID = "@Chelsea"


def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown&disable_notification=True".format(chat_id, photo_link, caption)
    dp.get_url(url)


def main():
    europe_timezone = pytz.timezone('Etc/GMT-1')
    date_baseline = datetime(2018, 5, 22, 15, 58, 18, tzinfo=europe_timezone)
    caption_store = []
    image_store = []
    while True:
        print("new pivot", datetime.now())
        news_url = drp.parsing_news()
        print(news_url['date'], "Date of last post")
        if news_url['date'] > date_baseline:
            if re.match(r'.*/sport/.*', news_url['link']):
                print("link is sport")
                last_news_info = dp.get_content(news_url['link'])
                last_caption = last_news_info['caption']
                last_image = last_news_info['image']

                if not re.match(r'.*Transfer [n, N]ews (LIVE|RECAP):.*', last_caption):
                    if (last_caption not in caption_store) and (last_image not in image_store):

                        message_text = "_@Chelsea NEWS:_ \n" + "*" + last_caption + "." + "*"
                        send_photo(CHAT_ID, last_image, message_text)
                        date_baseline = news_url['date']

                        caption_store.append(last_caption)
                        if len(caption_store) > 30:
                            caption_store.pop(0)
                        image_store.append(last_image)
                        if len(image_store) > 30:
                            image_store.pop(0)
        time.sleep(31)


if __name__ == '__main__':
    main()
