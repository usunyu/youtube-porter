from porter.utils import *
from porter.models import PorterJob, ManualMergeJob, Video, VideoTag, YoutubeAccount
from porter.enums import PorterStatus, VideoSource
from porter.downloaders.url_downloader import url_download

TAG = '[KUAIYINSHI MERGER]'


VIDEO_WIDTH = 2276
VIDEO_HEIGHT = 1280

def kuaiyinshi_video_merge():
    # try get first pending manual merge job
    manual_merge_job = ManualMergeJob.objects.filter(status=PorterStatus.PENDING).first()
    if not manual_merge_job:
        return
    # parse porter job id list
    porter_job_list = manual_merge_job.job_id_list.split(',')
    # parse thumbnail job id list
    thumbnail_job_list = manual_merge_job.thumbnail_id_list.split(',')
    # check if job is pending for merge
    merge_ready = True
    account = None
    for job_id in porter_job_list:
        job = PorterJob.objects.get(pk=job_id)
        if not account:
            account = job.youtube_account
        if job.status != PorterStatus.PENDING_MERGE:
            merge_ready = False
        if job.status == PorterStatus.PENDING_REVIEW:
            # already reviewed, update status to *PENDING*
            job.status = PorterStatus.PENDING
            job.save(update_fields=['status'])
    if not merge_ready:
        return
    manual_merge_job.status = PorterStatus.DOWNLOADING
    manual_merge_job.save(update_fields=['status'])
    porter_video = Video(url='-',
                         title=manual_merge_job.video_title,
                         category='Entertainment')
    porter_video.save()
    tag_names = manual_merge_job.video_tags.split(',')
    for tag_name in tag_names:
        tag = VideoTag.objects.filter(name=tag_name).first()
        if not tag:
            # create the tag
            tag = VideoTag(name=tag_name)
            tag.save()
        porter_video.tags.add(tag)
    # create upload porter job
    porter_job = PorterJob(video_url='-',
                           youtube_account=account,
                           video=porter_video,
                           video_source=manual_merge_job.video_source,
                           status=PorterStatus.DOWNLOADING)
    porter_job.save()
    # merging video
    pending_videos = []
    for job_id in porter_job_list:
        job = PorterJob.objects.get(pk=job_id)
        # resize video
        resize_file = get_random_16_code() + '.mp4'
        resize_video(job.video_file, VIDEO_WIDTH, VIDEO_HEIGHT, resize_file)
        pending_videos.append(resize_file)
    merged_video = get_random_16_code() + '.mp4'
    try:
        merge_videos(pending_videos, merged_video)
    except:
        print_log(TAG, 'Merge videos exception!')
        manual_merge_job.status = PorterStatus.FAILED
        manual_merge_job.save(update_fields=['status'])
        return
    # merged
    for job_id in porter_job_list:
        job = PorterJob.objects.get(pk=job_id)
        # update job status to *MERGED*
        job.status = PorterStatus.MERGED
        job.save(update_fields=['status'])
    porter_job.video_file = merged_video
    # generate thumbnail
    pending_thumbnails = []
    for thumb_id in thumbnail_job_list:
        job = PorterJob.objects.get(pk=thumb_id)
        thumbnail_file = url_download(job.thumbnail_url)
        job.thumbnail_file = thumbnail_file
        job.save(update_fields=['thumbnail_file'])
        pending_thumbnails.append(thumbnail_file)
    final_thumbnail = None
    # 1 thumbnail or 3 thumbnails
    if len(pending_thumbnails) == 1:
        final_thumbnail = pending_thumbnails[0]
    elif len(pending_thumbnails) == 3:
        # merge 3 thumbnails
        final_thumbnail = get_random_16_code() + '.jpeg'
        try:
            merge_images(pending_thumbnails, final_thumbnail)
        except:
            print_exception(TAG, 'Merge thumbnails exception!')
            final_thumbnail = None
    if final_thumbnail:
        porter_job.thumbnail_file = final_thumbnail

    # update final job status to *DOWNLOADED*
    porter_job.status = PorterStatus.DOWNLOADED
    porter_job.save(update_fields=['video_file', 'thumbnail_file', 'status'])

    manual_merge_job.merge_at = get_current_time()
    manual_merge_job.status = PorterStatus.SUCCESS
    manual_merge_job.save(update_fields=['status', 'merge_at'])


TEN_MINUTES = 600

# use manual merge job
def video_merge_DEPRECATED(source=VideoSource.DOUYIN):
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
        porter_video = Video(url='-', category='Entertainment')
        porter_video.save()
        porter_job = PorterJob(video_url='-',
                  youtube_account=account,
                  video=porter_video,
                  video_source=source,
                  status=PorterStatus.DOWNLOADING)
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
        # add video title
        for job in top_3_jobs:
            if job.video.title:
                porter_video.title = job.video.title
                porter_video.save(update_fields=['title'])
                break
        # TODO, fetch more accurate tags
        tag_names = ['搞笑', '美女', '短视频', '合集', '热门', '抖音', 'Tik Tok', 'Funny', 'Beauty', 'Short video', 'Featured']
        for tag_name in tag_names:
            tag = VideoTag.objects.filter(name=tag_name).first()
            if not tag:
                # create the tag
                tag = VideoTag(name=tag_name)
                tag.save()
            porter_video.tags.add(tag)
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
        for i in range(0, len(merge_jobs)):
            job = merge_jobs[i]
            # resize video
            resize_file = 'resizevideo' + str(i) + '.mp4'
            print_log(TAG, 'Resizing video {}/{}'.format(i + 1, len(merge_jobs)))
            resize_video(job.video_file, VIDEO_WIDTH, VIDEO_HEIGHT, resize_file)
            pending_videos.append(resize_file)
            # update job status to *MERGED*
            job.status = PorterStatus.MERGED
            job.save(update_fields=['status'])
        merged_video = get_random_16_code() + '.mp4'
        merge_videos(pending_videos, merged_video)
        porter_job.video_file = merged_video
        # update final job status to *DOWNLOADED*
        porter_job.status = PorterStatus.DOWNLOADED
        porter_job.save(update_fields=['video_file', 'status'])
