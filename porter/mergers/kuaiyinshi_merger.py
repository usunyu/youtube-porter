from porter.utils import *
from porter.models import PorterJob, YoutubeAccount
from porter.enums import PorterStatus, VideoSource
from porter.downloaders.url_downloader import url_download

TAG = '[KUAIYINSHI MERGER]'


TEN_MINUTES = 600

def video_merge(source):
    # all jobs needs merge
    pending_jobs = PorterJob.objects.filter(
        Q(video_source=source) &
        Q(status=PorterStatus.PENDING_MERGE))
    total_duration = 0
    # check if videos has enough duration
    merge_jobs = []
    for job in pending_jobs:
        total_duration += job.video.duration
        merge_jobs.append(job)
        if total_duration >= TEN_MINUTES:
            break
    # should merge video and create porter job
    if total_duration >= TEN_MINUTES:
        # upload to yporttiktok account
        # account = get_youtube_yporttiktok_account()
        # TODO, this is for testing
        account = get_youtube_test_account()
        porter_job = PorterJob(video_url='-',
                  youtube_account=account,
                  video_source=source)
        porter_job.save()

        top_3_jobs = []
        # find top 3 video and merge thumbnail
        for job in merge_jobs:
            # fill the top 3 first
            if len(top_3_jobs) < 3:
                top_3_jobs.append(job)
                continue
            # find the lowest score job in top 3
            lowest_index = 0
            for i in range(1, len(top_3_jobs)):
                if get_video_job_score(top_3_jobs[lowest_index]) > get_video_job_score(top_3_jobs[i]):
                    lowest_index = i
            # check if current job is higher than lowest in top 3
            if get_video_job_score(job) > get_video_job_score(top_3_jobs[lowest_index]):
                # replace the job
                top_3_jobs[lowest_index] = job
        # process thumbnail
        if len(top_3_jobs) == 3:
            # download top 3 thumbnails
            top_3_thumbnails = []
            for top_job in top_3_jobs:
                thumbnail_file = url_download(top_job.thumbnail_url)
                top_job.thumbnail_file = thumbnail_file
                top_job.save(update_fields=['thumbnail_file'])
                top_3_thumbnails.append(thumbnail_file)
            # merge top 3 thumbnails
            merged_thumbnail = get_random_16_code() + '.jpeg'
            merge_images(top_3_thumbnails, merged_thumbnail)
            porter_job.thumbnail_file = merged_thumbnail
            porter_job.save(update_fields=['thumbnail_file'])
        # merge videos
        pending_videos = []
        for job in pending_jobs:
            pending_videos.append(job.video_file)
        merged_video = get_random_16_code() + '.mp4'
        merge_videos(pending_videos, merged_video)
        porter_job.video_file = merged_video
        porter_job.save(update_fields=['video_file'])


def douyin_video_merge():
    video_merge(VideoSource.DOUYIN)
