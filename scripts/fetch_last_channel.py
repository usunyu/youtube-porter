# -*- coding: utf-8 -*-
'''
Fetch the last added channel jobs.
'''
from porter.utils import *
from porter.enums import VideoSource
from porter.models import ChannelJob
from porter.fetchers.bilibili_fetcher import bilibili_channel_fetch

job = ChannelJob.objects.last()

if job:
    if job.video_source == VideoSource.BILIBILI:
        bilibili_channel_fetch(job)
