# - *- coding: utf- 8 - *-
import requests, json, re


def download(url):
    local_filename = 'av2663796.flv'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(url, headers=headers, stream=True)
    file = open(local_filename, 'wb')
    print('downloading...')
    for chunk in response.iter_content(chunk_size=1024):
        if chunk: # filter out keep-alive new chunks
            file.write(chunk)
            # file.flush()
    file.close()
    print('download finish')


BILIBILI_API = 'https://www.kanbilibili.com/api/video/'

video_url = 'https://www.bilibili.com/video/av2663796'
aid = re.findall('.*av([0-9]+)', video_url)[0]
api_url = 'https://www.kanbilibili.com/api/video/' + aid

response = requests.get(api_url)
# print(response.text)
payload = json.loads(response.text)

if payload['err'] == None:
    data = payload['data']
    # default first page
    ls = data['list'][0]
    cid = ls['cid']
    d_api_url = api_url + '/download?cid=' + str(cid) + '&quality=48'
    d_response = requests.get(d_api_url)
    # print(d_response.text)
    d_payload = json.loads(d_response.text)
    download_url = d_payload['data']['durl'][0]['url']
    # print(download_url)
    download(download_url)
