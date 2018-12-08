#!/usr/bin/python
import subprocess, json
from porter.utils import *
from porter.models import PorterJob, Video, VideoSource, PorterStatus

TAG = '[DOUYIN FETCHER]'

def douyin_channel_fetch(job):
    channel_url = job.url
    channel_name = job.name
    account = job.youtube_account
    fetch_commend = 'tiktok-crawler ' + channel_url

    # this channel already fetched before
    if job.last_fetched_at:
        # only fetch first page
        fetch_commend += ' latest'
    else:
        # this channel not fetched before
        fetch_commend += ' all'

    try:
        output = subprocess.check_output(fetch_commend, shell=True)
        output = output.decode('utf-8')
    except:
        print_exception(TAG, 'Fetch Douyin channel: ' + channel_url + ' exception!')
        print_log(TAG, 'Fetch Douyin channel: ' + channel_url + ' exception!')
        return

    json_data = json.loads(output)
    video_list = json_data.get('list', [])

    # create porter job
    added_jobs = 0
    for video in video_list:
        video_title = video.get('desc', '')
        download_url = video.get('video_url', '')
        thumbnail_url = video.get('image_url', '')
        like_count = video.get('like', 0)
        share_count = video.get('share', 0)

        if PorterJob.objects.filter(
            Q(download_url=download_url) &
            Q(youtube_account=account)
        ).exists():
            continue
        added_jobs = added_jobs + 1
        video = Video(url='-', title=video_title)
        video.save()
        PorterJob(video_url='-',
                  download_url=download_url,
                  thumbnail_url=thumbnail_url,
                  playlist=channel_name,
                  video=video,
                  video_source=VideoSource.DOUYIN,
                  status=PorterStatus.PENDING_REVIEW,
                  youtube_account=account).save()
    print_log(TAG, 'Create {} new jobs from channel {}'.format(added_jobs, channel_name))

    # update last fetched time
    job.last_fetched_at = get_current_time()
    job.save(update_fields=['last_fetched_at'])
