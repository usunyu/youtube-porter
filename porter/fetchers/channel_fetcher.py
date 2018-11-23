from django.db.models import Q
from porter.utils import *
from porter.enums import VideoSource
from porter.models import PorterJob, ChannelJob
from porter.fetchers.bilibili_fetcher import bilibili_channel_fetch


DELAY_INTERVAL = 5

def channel_fetch():
    jobs = ChannelJob.objects.filter(active=True)
    for job in jobs:
        account = job.youtube_account
        fetched_videos = []
        if job.video_source == VideoSource.BILIBILI:
            fetched_videos = bilibili_channel_fetch(job)
        for video_url in fetched_videos:
            if PorterJob.objects.filter(
                Q(video_url=video_url) &
                Q(youtube_account=account)
            ).exists():
                continue
            # print_log(TAG, 'Create new job from channel fetch: ' + video_url)
            PorterJob(video_url=video_url, youtube_account=account).save()
        time.sleep(DELAY_INTERVAL)
