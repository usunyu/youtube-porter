from porter.utils import *
from porter.enums import PorterStatus
from porter.downloaders.url_downloader import url_download

TAG = '[KUAIYINSHI MERGER]'


TEN_MINUTES = 600

def video_merge(source):
    # all jobs needs merge
    douyin_jobs = PorterJob.objects.filter(
        Q(video_source=source) &
        Q(status=PorterStatus.PENDING_MERGE))
    total_duration = 0
    # check if videos has enough duration
    merge_jobs = []
    for job in douyin_jobs:
        total_duration += job.video.duration
        merge_jobs.append(job)
        if total_duration >= TEN_MINUTES:
            break
    if total_duration >= TEN_MINUTES:
        top_3 = []
        # find top 3 video and merge thumbnail
        for job in merge_jobs:
            # fill the top 3 first
            if len(top_3) < 3:
                top_3.append(job)
                continue
            # find the lowest score job in top 3
            lowest_index = 0
            for i in range(1, len(top_3)):
                if get_video_job_score(top_3[lowest_index]) > get_video_job_score(top_3[i]):
                    lowest_index = i
            # check if current job is higher than lowest in top 3
            if get_video_job_score(job) > get_video_job_score(top_3[lowest_index]):
                # replace the job
                top_3[lowest_index] = job
        if len(top_3) == 3:
            merged_thumbnail = get_time_str() + '.jpeg'
            # TODO, download top 3 thumbnails
            # merge_images([top_3[]], merged_thumbnail)

        # TODO, merge videos

def douyin_video_merge():
    video_merge(VideoSource.DOUYIN)
