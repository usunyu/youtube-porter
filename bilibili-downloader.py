# - *- coding: utf- 8 - *-
import requests, json, re

CHUNK_SIZE = 1024

def download(url, filename='0'):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers['content-length'])
    format = response.headers['Content-Type']
    if format=='video/mp4':
        local_filename = filename + '.mp4'
    else:
        local_filename = filename + '.flv'
    file = open(local_filename, 'wb')
    print('Start downloading...')
    download_size = 0
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk: # filter out keep-alive new chunks
            file.write(chunk)
            # file.flush()
        download_size = download_size + CHUNK_SIZE
        end = '\r'
        if download_size > total_size:
            download_size = total_size
            end = '\r\n'
        print('Download progress: {:.0%}'.format(float(download_size) / total_size), end=end, flush=True),
    file.close()
    print('Download finish!')


BILIBILI_API = 'https://www.kanbilibili.com/api/video/'

video_url = 'https://www.bilibili.com/video/av2663796'
video_id = re.findall('.*av([0-9]+)', video_url)[0]
api_url = 'https://www.kanbilibili.com/api/video/' + video_id

response = requests.get(api_url)
# print(response.text)
payload = json.loads(response.text)

if payload['err'] == None:
    data = payload['data']
    # TODO save video info
    title = data['title']
    typename = data['typename']
    description = data['description']

    # default first page
    ls = data['list'][0]
    cid = ls['cid']
    d_api_url = api_url + '/download?cid=' + str(cid) + '&quality=48'
    d_response = requests.get(d_api_url)
    # print(d_response.text)
    d_payload = json.loads(d_response.text)
    download_url = d_payload['data']['durl'][0]['url']
    # print(download_url)
    download(download_url, str(video_id))
