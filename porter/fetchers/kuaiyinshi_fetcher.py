import requests, json, re, time
from django.db.models import Q
from porter.utils import *
from porter.models import PorterJob, Video, YoutubeAccount
from porter.enums import VideoSource, PorterJobType


TAG = '[KUAIYINSHI FETCHER]'

KUAIYINSHI_RECOMMEND_API = 'https://kuaiyinshi.com/api/hot/videos/?source={}&page={}&st={}'

DELAY_INTERVAL = 5

def douyin_recommend_fetch():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(KUAIYINSHI_RECOMMEND_API.format('dou-yin', 1, 'day'), headers=headers)
    payload = json.loads(response.text)

    if payload['code'] == 200:
        data = payload['data']

        # upload to yporttiktok account
        # account = get_youtube_yporttiktok_account()
        # TODO, this is for testing
        account = get_youtube_test_account()
        added_jobs = 0
        for record in data:
            download_url = 'http:' + record['video_url']
            if PorterJob.objects.filter(
                Q(download_url=download_url) &
                Q(youtube_account=account)
            ).exists():
                continue
            title = record['desc']
            statistics = record['statistics']
            likes = statistics['zan']
            comments = statistics['comment']
            shares = statistics['share']
            thumbnail_url = 'http:' + record['video_img']
            video = Video(url='-', title=title)
            video.save()
            PorterJob(video_url='-',
                      download_url=download_url,
                      thumbnail_url=thumbnail_url,
                      youtube_account=account,
                      video_source=VideoSource.DOUYIN,
                      video=video,
                      type=PorterJobType.MERGE,
                      likes=likes,
                      comments=comments,
                      shares=shares).save()
            added_jobs = added_jobs + 1
        print_log(TAG, 'Create {} new jobs from Douyin'.format(added_jobs))


def douyin_channel_fetch(job):
    # TODO
    pass
