import os, subprocess, requests, json
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Q
from porter.utils import *
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.channel_fetchers.bilibili_channel_fetcher import bilibili_channel_fetch
from porter.enums import VideoSource, PorterStatus
from porter.models import Video, YoutubeAccount, PorterJob, ChannelJob


TAG = '[SCHEDULERS]'

# set small for debug
# JOB_INTERVAL_UNIT = 1
JOB_INTERVAL_UNIT = 60 # 1 minute
DOWNLOAD_JOB_INTERVAL = 3.2 * JOB_INTERVAL_UNIT
UPLOAD_JOB_INTERVAL = 2.1 * JOB_INTERVAL_UNIT
CHANNEL_JOB_INTERVAL = 60 * 12 * JOB_INTERVAL_UNIT

YOUTUBE_UPLOAD_QUOTA = 98

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

download_job_lock = False
upload_job_lock = False

BILIBILI_VIDEO_URL = 'https://www.bilibili.com/video/av{}'
BILIBILI_RECOMMEND_API = 'http://api.bilibili.cn/recommend'

VIDEO_DESCRIPTION = """All videos are from online resources. If you find a video that infringes on your rights, please contact yportmaster@gmail.com to delete the video.
If you like this video, please like, comment and subscribe. Thank you!
(所有视频均来自网络资源, 如果侵犯了您的权益请联系yportmaster@gmail.com删除视频.
如果您喜欢此视频, 请点赞, 留言, 订阅. 非常感谢!)


This video is from: {}

Video description:
{}
"""

@scheduler.scheduled_job("interval", seconds=DOWNLOAD_JOB_INTERVAL, id='download')
def download_job():
    if not is_start_download_job():
        # print_log(TAG, 'Download job is stopped, skip this schedule...')
        return

    # find a job with account has quota
    job = None
    pending_jobs = PorterJob.objects.filter(status=PorterStatus.PENDING)
    for pending_job in pending_jobs:
        if pending_job.youtube_account.upload_quota > 0:
            job = pending_job
            break
    if not job:
        print_log(TAG, 'No pending download job available, skip this schedule...')
        return

    global download_job_lock

    if download_job_lock:
        print_log(TAG, 'Download job is still running, skip this schedule...')
        return

    print_log(TAG, 'Download job is started...')

    # check if job is duplicated
    if PorterJob.objects.filter(
        Q(video_url=job.video_url) &
        Q(youtube_account=job.youtube_account) &
        Q(status=PorterStatus.SUCCESS)
    ).exists():
        # update status to *DUPLICATED*
        job.status = PorterStatus.DUPLICATED
        job.save(update_fields=['status'])
        print_log(TAG, 'Download job is duplicated, skip this schedule...')
        return

    download_job_lock = True

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
        video_file = bilibili_download(job)
    else:
        video_file = None

    if video_file:
        # update job video file
        job.video_file = video_file
        job.download_at = get_current_time()
        # update status to *DOWNLOADED*
        job.status = PorterStatus.DOWNLOADED
        job.save(update_fields=['video_file', 'status', 'download_at'])
    else:
        # update status to *DOWNLOAD_FAIL*
        job.status = PorterStatus.DOWNLOAD_FAIL
        job.save(update_fields=['status'])

    download_job_lock = False


@scheduler.scheduled_job("interval", seconds=UPLOAD_JOB_INTERVAL, id='upload')
def upload_job():
    if not is_start_upload_job():
        # print_log(TAG, 'Upload job is stopped, skip this schedule...')
        return

    # find a job with account has quota
    job = None
    downloaded_jobs = PorterJob.objects.filter(status=PorterStatus.DOWNLOADED)
    for downloaded_job in downloaded_jobs:
        if downloaded_job.youtube_account.upload_quota > 0:
            job = downloaded_job
            break
    if not job:
        print_log(TAG, 'No pending upload job available, skip this schedule...')
        return

    global upload_job_lock

    if upload_job_lock:
        print_log(TAG, 'Upload job is still running, skip this schedule...')
        return

    print_log(TAG, 'Upload job is started...')

    upload_job_lock = True

    video = job.video
    youtube_account = job.youtube_account

    print_log(TAG, 'Start to upload job: ' + str(job.id))
    print_log(TAG, 'Video: ' + video.title)
    print_log(TAG, 'Youtube account: ' + youtube_account.name)

    try:
        # update status to *UPLOADING*
        job.status = PorterStatus.UPLOADING
        job.save(update_fields=['status'])
        print_log(TAG, '******************************************')
        print_log(TAG, '*      You may need input password!      *')
        print_log(TAG, '******************************************')
        # upload to youtube
        upload_command = 'sudo youtube-upload --title="{}" --description="{}" --category="{}" --tags="{}" --client-secrets="{}" "{}"'.format(
            video.title,
            VIDEO_DESCRIPTION.format(video.url, video.description),
            video.category,
            video.print_tags(),
            youtube_account.secret_file,
            job.video_file
        )
        if job.playlist:
            upload_command = upload_command + ' --playlist="' + job.playlist + '"'
        output = subprocess.check_output(upload_command, shell=True)
        youtube_id = output.decode("utf-8").strip()
        job.youtube_id = youtube_id
        job.upload_at = get_current_time()
        # update status to *SUCCESS*
        job.status = PorterStatus.SUCCESS
        job.save(update_fields=['youtube_id', 'status', 'upload_at'])
        youtube_account.upload_quota = youtube_account.upload_quota - 1
        youtube_account.save(update_fields=['upload_quota'])

    except Exception as e:
        print_log(TAG, 'Failed to upload video: ' + video.title)
        print_log(TAG, str(e))
        # update status to *UPLOAD_FAIL*
        job.status = PorterStatus.UPLOAD_FAIL
        job.save(update_fields=['status'])
    # clean video file
    try:
        os.remove(job.video_file)
        print_log(TAG, 'Deleted video: ' + job.video_file)
    except Exception as e:
        print_log(TAG, 'Failed to delete video: ' + job.video_file)
        print_log(TAG, str(e))

    upload_job_lock = False


@scheduler.scheduled_job("interval", seconds=CHANNEL_JOB_INTERVAL, id='channel')
def channel_job():
    if not is_start_channel_job():
        # print_log(TAG, 'Channel job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Channel job is started...')

    jobs = ChannelJob.objects.all()
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
            print_log(TAG, 'Create new job from channel fetch: ' + video_url)
            PorterJob(video_url=video_url, youtube_account=account).save()


@scheduler.scheduled_job("cron", hour=0, minute=30, id='bilibili_recommend', misfire_grace_time=60, coalesce=True)
def bilibili_recommend_job():
    if not is_start_bilibili_recommend_job():
        # print_log(TAG, 'Bilibili recommend job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Bilibili recommend job is started...')
    response = requests.get(BILIBILI_RECOMMEND_API)
    list = json.loads(response.text)['list']

    # default to first account
    account = YoutubeAccount.objects.all().first()

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


@scheduler.scheduled_job("cron", hour=14, minute=30, id='reset_quota', misfire_grace_time=60, coalesce=True)
def reset_quota_job():
    if not is_start_reset_quota_job():
        # print_log(TAG, 'Reset quota job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Reset quota job is started...')
    accounts = YoutubeAccount.objects.all()
    for account in accounts:
        account.upload_quota = YOUTUBE_UPLOAD_QUOTA
        account.save(update_fields=['upload_quota'])


# avoid multi-thread to start multiple schedule jobs
import fcntl
try:
    lock = open('lock.obj', 'w+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    print_log(TAG, 'Schedule job started!')
    register_events(scheduler)
    scheduler.start()
except IOError as e:
    print_log(TAG, 'Schedule job already start, skip...')
