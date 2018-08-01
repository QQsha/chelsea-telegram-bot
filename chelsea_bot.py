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
#CHAT_ID = "-1001279121498"


def send_photo(chat_id, photo_link, caption):
    caption = urllib.parse.quote_plus(caption)
    url = URL + "sendPhoto?chat_id={}&photo={}&caption={}&parse_mode=Markdown&disable_notification=True".format(chat_id, photo_link, caption)
    dp.get_url(url)

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
                last_news_info = dp.get_content(news_url['link'])
                last_caption = last_news_info['caption']
                last_image = last_news_info['image']

                if not re.match(r'.*Transfer [n, N]ews (LIVE|RECAP):.*', last_caption):
                    if same_text(caption_store, last_caption):
                        message_text = "@like Chelsea _NEWS:_ \n" + "*" + last_caption + "." + "*"
                        send_photo(CHAT_ID, last_image, message_text)
                        date_baseline = news_url['date']

                        caption_store.append(last_caption.split(' '))
                        if len(caption_store) > 20:
                            caption_store.pop(0)

        time.sleep(45)


if __name__ == '__main__':
    main()
