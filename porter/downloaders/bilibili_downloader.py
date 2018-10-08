import requests, json, re
from requests_html import HTMLSession
from porter.utils import print_log, get_time_str
from porter.models import VideoTag


TAG = '[BILIBILI DOWNLOADER]'

BILIBILI_API = 'https://www.kanbilibili.com/api/video/'

CHUNK_SIZE = 1024

def download(url):
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
        response = requests.get(url, headers=headers, stream=True)
        total_size = int(response.headers['content-length'])
        format = response.headers['Content-Type']
        filename = get_time_str()
        if format=='video/mp4':
            filename = filename + '.mp4'
        else:
            filename = filename + '.flv'
        file = open(filename, 'wb')
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
        return filename
    except Exception as e:
        print_log(TAG, 'Unknown error during bilibili download!')
        print(e)
        return None

def bilibili_download(job):
    video_url = job.video_url
    video_id = re.findall('.*av([0-9]+)', video_url)[0]
    api_url = BILIBILI_API + video_id
    print_log(TAG, 'Fetch data from ' + api_url)
    response = requests.get(api_url)
    payload = json.loads(response.text)

    if payload['err'] == None:
        data = payload['data']
        video = job.video
        title = data['title']
        video.title = title
        print_log(TAG, 'Title: ' + title)
        typename = data['typename']
        print_log(TAG, 'Typename: ' + typename)
        description = data['description']
        video.description = description
        print_log(TAG, 'Description: ' + description)
        # fetch video tags
        html_session = HTMLSession()
        html_response = html_session.get(video_url)
        html_tags = []
        try:
            html_tags = html_response.html.find('#v_tag', first=True).find('.tag')
        except Exception as ex:
            print_log(TAG, 'Error during fetching tags for this video!')
        for html_tag in html_tags:
            tag_name = html_tag.text
            # check if tag exists
            tag = VideoTag.objects.filter(name=tag_name).first()
            if not tag:
                # create the tag
                tag = VideoTag(name=tag_name)
                tag.save()
            video.tags.add(tag)
        video.save(update_fields=['title', 'description'])

        # default first page
        # TODO deal with multi page video
        ls = data['list'][0]
        cid = ls['cid']
        # quality:
        # 112: 1080P+
        # 80: 1080P
        # 64: 720P
        # 32: 480P
        # 15: 360P
        # default to highest quality
        d_api_url = api_url + '/download?cid=' + str(cid) + '&quality=112'
        d_response = requests.get(d_api_url)
        d_payload = json.loads(d_response.text)
        download_url = d_payload['data']['durl'][0]['url']
        print_log(TAG, 'Ready to download video from: ' + download_url)
        return download(download_url)

    print_log(TAG, 'Fetch data error!')
    return None
