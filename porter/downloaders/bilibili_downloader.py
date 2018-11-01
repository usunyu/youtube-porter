import requests, json, re, os, subprocess
from requests_html import HTMLSession
from porter.utils import *
from porter.models import VideoTag, PorterJob
from porter.enums import VideoSource, PorterStatus, PorterJobType
from porter.downloaders.url_downloader import url_download


TAG = '[BILIBILI DOWNLOADER]'

BILIBILI_API = 'https://www.kanbilibili.com/api/video/'

# use bilibili-get for stable download
def bilibili_download_DEPRECATED(job):
    video_url = job.video_url
    video_id = re.findall('.*av([0-9]+)', video_url)[0]
    api_url = BILIBILI_API + video_id
    print_log(TAG, 'Fetch data from ' + api_url)
    try:
        response = requests.get(api_url)
    except Exception as e:
        print_log(TAG, 'Request api error!')
        return None
    payload = json.loads(response.text)

    if payload['err'] == None:
        data = payload['data']
        video = job.video
        if 'title' in data:
            title = data['title']
        else:
            print_log(TAG, 'This video may be removed!')
            return None
        typename = ''
        if 'typename' in data:
            typename = data['typename']
        description = ''
        if 'description' in data:
            description = data['description']
        for invalid_char in get_youtube_invalid_content_chars():
            title = title.replace(invalid_char, '')
            description = description.replace(invalid_char, '')
        video.title = title
        video.description = description

        print_log(TAG, 'Title: ' + title)
        print_log(TAG, 'Typename: ' + typename)
        print_log(TAG, 'Description: ' + description)

        # fetch video tags
        html_session = HTMLSession()
        html_response = html_session.get(video_url)
        html_tags = []
        try:
            html_tags = html_response.html.find('#v_tag', first=True).find('.tag')
        except Exception as e:
            print_log(TAG, 'Error during fetching tags for this video!')
            print_log(TAG, str(e))
        for html_tag in html_tags:
            tag_name = html_tag.text
            for invalid_char in get_youtube_invalid_tag_chars():
                tag_name = tag_name.replace(invalid_char, '')
            # check if tag exists
            tag = VideoTag.objects.filter(name=tag_name).first()
            if not tag:
                # create the tag
                tag = VideoTag(name=tag_name)
                tag.save()
            video.tags.add(tag)
        video.save(update_fields=['title', 'description'])

        # default first page
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
        d_data = d_payload['data']
        if not 'durl' in d_data:
            print_log(TAG, 'This video may be deleted!')
            return None
        download_url = d_data['durl'][0]['url']
        print_log(TAG, 'Ready to download video from: ' + download_url)
        return url_download(download_url)

    print_log(TAG, 'Fetch data error!')
    return None

def bilibili_download(job):
    video_url = job.video_url
    video_id = re.findall('.*av([0-9]+)', video_url)[0]
    api_url = BILIBILI_API + video_id
    print_log(TAG, 'Fetch data from ' + api_url)
    try:
        response = requests.get(api_url)
    except Exception as e:
        print_log(TAG, 'Request api exception!')
        print_log(TAG, str(e))
        return [PorterStatus.API_EXCEPTION, None]
    payload = json.loads(response.text)

    if payload['err'] == None:
        data = payload['data']
        video = job.video
        if 'title' in data:
            title = data['title']
        else:
            print_log(TAG, 'This video may be removed!')
            return [PorterStatus.VIDEO_NOT_FOUND, None]
        typename = ''
        if 'typename' in data:
            typename = data['typename']
        description = ''
        if 'description' in data:
            description = data['description']
        for invalid_char in get_youtube_invalid_content_chars():
            title = title.replace(invalid_char, '')
            description = description.replace(invalid_char, '')
        part = job.part
        if job.type == PorterJobType.PARTIAL:
            vlist = data['list']
            vdata = vlist[part - 1]
            # update title with part information
            title = title + ' ' + vdata['part']
            video_url = video_url + '?p=' + str(part)

        video.title = title
        video.description = description

        print_log(TAG, 'Title: ' + title)
        print_log(TAG, 'Typename: ' + typename)
        print_log(TAG, 'Description: ' + description)

        # fetch video tags
        html_session = HTMLSession()
        html_response = html_session.get(video_url)
        html_tags = []
        try:
            html_tags = html_response.html.find('#v_tag', first=True).find('.tag')
        except Exception as e:
            print_log(TAG, 'Error during fetching tags for this video!')
            print_log(TAG, str(e))
        for html_tag in html_tags:
            tag_name = html_tag.text
            for invalid_char in get_youtube_invalid_tag_chars():
                tag_name = tag_name.replace(invalid_char, '')
            # check if tag exists
            tag = VideoTag.objects.filter(name=tag_name).first()
            if not tag:
                # create the tag
                tag = VideoTag(name=tag_name)
                tag.save()
            video.tags.add(tag)
        video.save(update_fields=['title', 'description'])

        # update video statistics
        try:
            job.views = data['play']
        except Exception:
            job.views = 0
        try:
            job.likes = data['coins']
        except Exception:
            job.likes = 0
        job.save(update_fields=['views', 'likes'])

        # check if video has multi part
        pages = 1
        if 'pages' in data:
            pages = data['pages']
        if pages > 1 and job.type == PorterJobType.COMPLETE:
            part = 1
            while part <= pages:
                # create partial porter job
                PorterJob(video_url=video_url,
                          youtube_account=job.youtube_account,
                          video_source=VideoSource.BILIBILI,
                          playlist=video.title,
                          type=PorterJobType.PARTIAL,
                          part=part).save()
                part = part + 1
            print_log(TAG, 'Added partial {} jobs.'.format(pages))
            return [PorterStatus.PARTIAL, None]

        try:
            subprocess.run(['bilibili-get {} -o "av%(aid)s_{}.%(ext)s" -f flv'.format(video_url, part)], shell=True)
        except Exception as e:
            # may rase exception:
            # error parsing debug value
            # debug=0
            # if video is already downloaded, success
            if os.path.isfile('av{}_{}.flv'.format(video_id, part)):
                return [PorterStatus.DOWNLOADED, 'av{}_{}.flv'.format(video_id, part)]
            print_log(TAG, 'Download video failed, bilibili-get exception!')
            print_log(TAG, str(e))
            return [PorterStatus.DOWNLOAD_FAIL, None]

        # check download file success
        if not os.path.isfile('av{}_{}.flv'.format(video_id, part)):
            print_log(TAG, 'Download video failed, unknown error!')
            return [PorterStatus.DOWNLOAD_FAIL, None]

        return [PorterStatus.DOWNLOADED, 'av{}_{}.flv'.format(video_id, part)]

    print_log(TAG, 'Fetch data error!')
    return [PorterStatus.API_ERROR, None]
