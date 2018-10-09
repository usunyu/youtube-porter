# -*- coding: utf-8 -*-
'''
Parsing data from http://api.bilibili.cn/recommend and
creating corresponding PorterJob.
'''
import requests, json
from porter.models import PorterJob, YoutubeAccount

API_URL = 'http://api.bilibili.cn/recommend'
VIDEO_URL = 'https://www.bilibili.com/video/av'

print('Fetching data...')
response = requests.get(API_URL)
payload = json.loads(response.text)
pages = payload['pages']
num = payload['num']
print('Total pages:' + str(pages) + ', num: ' + str(num))

account = YoutubeAccount.objects.all().first()
print('Target account: ' + account.name)

print('Parsing data and creating jobs...')
page = pages
while page >= 1:
    api_url = '{}?page={}'.format(API_URL, page)
    res = requests.get(api_url)
    list = json.loads(res.text)['list']

    for record in list:
        aid = record['aid']
        # create porter job
        video_url = '{}{}'.format(VIDEO_URL, aid)
        PorterJob(video_url=video_url, youtube_account=account).save()

    page = page - 1

    progress = pages - page
    end = '\r'
    if progress == pages:
        end = '\r\n'
    print('Progress: {:.0%}'.format(float(progress) / pages), end=end, flush=True),
print('Done!')
