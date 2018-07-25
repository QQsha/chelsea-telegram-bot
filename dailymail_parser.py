import requests
import re


''' parsing news '''
URL = "http://www.dailymail.co.uk/sport/football/article-5756455/Chelsea-make-Robert-Lewandowski-summer-transfer-target.html?ITO=1490&ns_mchannel=rss&ns_campaign=1490"


PATTERN_IMAGE = r'og:image" content="(.*)"'
PATTERN_TITLE = r'.*<h2>(.*)</h2>'


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_content(url=URL):
    news = {}
    html = get_url(url)
    news['image'] = re.findall(PATTERN_IMAGE, html)[0]
    h2 = re.findall(PATTERN_TITLE, html)
    news['caption'] = h2[0]
    return news

get_content()
