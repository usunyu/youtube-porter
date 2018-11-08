from django.db.models import Q
from porter.utils import *
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.downloaders.kuaiyinshi_downloader import douyin_download
from porter.models import YoutubeAccount, PorterJob, Video
from porter.enums import PorterStatus, VideoSource


TAG = '[DOWNLOADER]'

MAX_DOWNLOAD_RETRIES = 3

def download(job):
    # check if job is duplicated
    if PorterJob.objects.filter(
        Q(video_url=job.video_url) &
        Q(youtube_account=job.youtube_account) &
        Q(status=PorterStatus.SUCCESS) &
        Q(type=job.type) &
        Q(part=job.part)
    ).exists():
        # update status to *DUPLICATED*
        job.status = PorterStatus.DUPLICATED
        job.save(update_fields=['status'])
        print_log(TAG, 'Download job is duplicated, download skipped...')
        return

    print_log(TAG, 'Start to download job: ' + str(job.id))
    print_log(TAG, 'Video url: ' + job.video_url)
    print_log(TAG, 'Video source: ' + VideoSource.tostr(job.video_source))
    print_log(TAG, 'Youtube account: ' + job.youtube_account.name)

    video = job.video
    if not video:
        # create video object if not existed
        video = Video(
            url=job.video_url,
            category='Entertainment' # default to entertainment category
        )
        video.save()
        job.video = video
        job.save(update_fields=['video'])
    # update status to *DOWNLOADING*
    job.status = PorterStatus.DOWNLOADING
    job.save(update_fields=['status'])
    # download the video
    if job.video_source == VideoSource.BILIBILI:
        download_status = bilibili_download(job)
    elif job.video_source == VideoSource.DOUYIN:
        download_status = douyin_download(job)
    else:
        download_status = PorterStatus.DOWNLOAD_FAIL

    # download video success
    if download_status == PorterStatus.DOWNLOADED:
        # update job video file
        job.download_at = get_current_time()
        job.save(update_fields=['download_at'])

    # download video failed, check retry
    if download_status == PorterStatus.DOWNLOAD_FAIL or download_status == PorterStatus.API_EXCEPTION:
        job.retried = job.retried + 1
        job.save(update_fields=['retried'])
        if job.retried < MAX_DOWNLOAD_RETRIES:
            # reset status to *PENDING*
            download_status = PorterStatus.PENDING

    # update status to corresponding status
    job.status = download_status
    job.save(update_fields=['status'])
