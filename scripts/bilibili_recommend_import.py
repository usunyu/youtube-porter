# -*- coding: utf-8 -*-
import requests, json
from porter.models import PorterJob

API_URL = 'http://api.bilibili.cn/recommend'

print('Fetching data...')

response = requests.get(API_URL)
payload = json.loads(response.text)

pages = payload['pages']
num = payload['num']

print('Total pages:' + str(pages) + ', num: ' + str(num))

list = payload['list']

print('Parsing data and creating jobs...')
page = pages
while page >= 1:
    api_url = '{}?page={}'.format(API_URL, page)
    res = requests.get(API_URL)
    data = json.loads(res.text)['list']

    page = page - 1

    progress = pages - page
    end = '\r'
    if progress == pages:
        end = '\r\n'
    print('Progress: {:.0%}'.format(float(progress) / pages), end=end, flush=True),

print('Done!')
