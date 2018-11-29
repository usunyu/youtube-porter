import time
from porter.utils import *
from porter.enums import VideoSource
from porter.models import ChannelJob
from porter.fetchers.bilibili_fetcher import bilibili_channel_fetch


DELAY_INTERVAL = 5

def channel_fetch():
    jobs = ChannelJob.objects.filter(active=True)
    for job in jobs:
        account = job.youtube_account
        if job.video_source == VideoSource.BILIBILI:
            bilibili_channel_fetch(job)

        time.sleep(DELAY_INTERVAL)
