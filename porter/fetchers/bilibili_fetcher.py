import requests, json, re, time
from django.db.models import Q
from porter.utils import *
from porter.models import PorterJob, YoutubeAccount


TAG = '[BILIBILI FETCHER]'

BILIBILI_CHANNEL_API = 'https://space.bilibili.com/ajax/member/getSubmitVideos?mid={}&pagesize=30&tid=0&page={}&keyword=&order=pubdate'
BILIBILI_RECOMMEND_API = 'http://api.bilibili.cn/recommend'
BILIBILI_VIDEO_URL = 'https://www.bilibili.com/video/av{}'

DELAY_INTERVAL = 5

def bilibili_channel_fetch(job):
    channel_url = job.url
    channel_id = re.findall('([0-9]+)', channel_url)[0]
    response = requests.get(BILIBILI_CHANNEL_API.format(channel_id, 1))
    payload = json.loads(response.text)
    account = job.youtube_account
    if not payload['status']:
        print_log(TAG, 'Fetch channel ' + channel_url + ' failed!')
        return []
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
            time.sleep(DELAY_INTERVAL)

    # create porter job
    added_jobs = 0
    for video in video_list:
        video_id = video['aid']
        video_url = BILIBILI_VIDEO_URL.format(video_id)
        if PorterJob.objects.filter(
            Q(video_url=video_url) &
            Q(youtube_account=account)
        ).exists():
            continue
        added_jobs = added_jobs + 1
        PorterJob(video_url=video_url,
                  playlist=job.name,
                  youtube_account=account).save()
    print_log(TAG, 'Create {} new jobs from channel {}'.format(added_jobs, job.name))

    # update last fetched time
    job.last_fetched_at = get_current_time()
    job.save(update_fields=['last_fetched_at'])


def bilibili_recommend_fetch():
    response = requests.get(BILIBILI_RECOMMEND_API)
    list = json.loads(response.text)['list']

    # upload to yportmaster account
    account = get_youtube_yportmaster_account()

    for record in list:
        video_id = record['aid']
        # create porter job
        video_url = BILIBILI_VIDEO_URL.format(video_id)
        if PorterJob.objects.filter(
            Q(video_url=video_url) &
            Q(youtube_account=account)
        ).exists():
            continue
        print_log(TAG, 'Create new job from bilibili recommend: ' + video_url)
        PorterJob(video_url=video_url, youtube_account=account).save()
