import requests, json, re
from django.db.models import Q
from porter.utils import *
from porter.models import PorterJob


TAG = '[BILIBILI CHANNEL]'

BILIBILI_CHANNEL_API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={}&pagesize=30&tid=0&page={}&keyword=&order=pubdate'
BILIBILI_VIDEO_URL = 'https://www.bilibili.com/video/av{}'

def bilibili_channel_fetch(job):
    channel_url = job.url
    channel_id = re.findall('([0-9]+)', channel_url)[0]
    response = requests.get(BILIBILI_CHANNEL_API.format(channel_id, 1))
    payload = json.loads(response.text)
    account = job.youtube_account
    if not payload['status']:
        print_log(TAG, 'Fetch channel ' + channel_url + ' failed!')
        return []
    fetched_videos = []
    video_list = []
    # this channel already fetched before
    if job.last_fetched_at:
        # only fetch first page
        vlist = json.loads(response.text)['data']['vlist']
        vlist.reverse()
        video_list = vlist
    else: # this channel not fetched before
        pages = payload['data']['pages']
        page = pages
        while page >= 1:
            api_url = BILIBILI_CHANNEL_API.format(channel_id, page)
            res = requests.get(api_url)
            vlist = json.loads(res.text)['data']['vlist']
            vlist.reverse()
            video_list.extend(vlist)
            page = page - 1

    # create porter job
    for video in video_list:
        video_id = video['aid']
        video_url = BILIBILI_VIDEO_URL.format(video_id)
        if PorterJob.objects.filter(
            Q(video_url=video_url) &
            Q(youtube_account=account)
        ).exists():
            continue
        print_log(TAG, 'Create new job from channel : ' + video_url)
        PorterJob(video_url=video_url,
                  playlist=job.name,
                  youtube_account=account).save()

    # update last fetched time
    job.last_fetched_at = get_current_time()
    job.save(update_fields=['last_fetched_at'])

    return fetched_videos
