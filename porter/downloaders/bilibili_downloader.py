import requests, json, re
from porter.utils import print_log, get_time_str


TAG = '[BILIBILI DOWNLOADER]'

BILIBILI_API = 'https://www.kanbilibili.com/api/video/'

CHUNK_SIZE = 1024

def download(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(url, headers=headers, stream=True)
    total_size = int(response.headers['content-length'])
    format = response.headers['Content-Type']
    filename = get_time_str()
    if format=='video/mp4':
        local_filename = filename + '.mp4'
    else:
        local_filename = filename + '.flv'
    file = open(local_filename, 'wb')
    print_log(TAG, 'Start downloading...')
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
        print(TAG, 'Download progress: {:.0%}'.format(float(download_size) / total_size), end=end, flush=True),
    file.close()
    print_log(TAG, 'Download finish!')

def bilibili_download(video_url):
    video_id = re.findall('.*av([0-9]+)', video_url)[0]
    api_url = BILIBILI_API + video_id
    print_log(TAG, 'Fetch data from ' + api_url)
    response = requests.get(api_url)
    payload = json.loads(response.text)

    if payload['err'] == None:
        data = payload['data']
        # TODO save video info
        title = data['title']
        print_log(TAG, 'Title: ' + title)
        typename = data['typename']
        print_log(TAG, 'Typename: ' + typename)
        description = data['description']
        print_log(TAG, 'Description: ' + description)

        # default first page
        # TODO deal with multi page video
        ls = data['list'][0]
        cid = ls['cid']
        d_api_url = api_url + '/download?cid=' + str(cid) + '&quality=48'
        d_response = requests.get(d_api_url)
        d_payload = json.loads(d_response.text)
        download_url = d_payload['data']['durl'][0]['url']
        print_log(TAG, 'Ready to download video from: ' + download_url)
        return download(download_url)

    print_log(TAG, 'Fetch data error!')
    return None
