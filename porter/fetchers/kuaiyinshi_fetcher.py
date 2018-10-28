import requests, json, re, time
from porter.utils import *
from porter.models import PorterJob, YoutubeAccount


TAG = '[KUAIYINSHI FETCHER]'

KUAIYINSHI_RECOMMEND_API = 'https://kuaiyinshi.com/api/hot/videos/?source={}&page={}&st={}'

DELAY_INTERVAL = 5

def douyin_recommend_fetch():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(KUAIYINSHI_RECOMMEND_API.format('dou-yin', 1, 'day'), headers=headers)
