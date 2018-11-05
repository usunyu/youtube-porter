import os, subprocess, requests, json, time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Q
from porter.utils import *
from porter.downloaders.downloader import download
from porter.fetchers.bilibili_fetcher import bilibili_channel_fetch, bilibili_recommend_fetch
from porter.fetchers.kuaiyinshi_fetcher import douyin_recommend_fetch
from porter.enums import VideoSource, PorterStatus
from porter.models import YoutubeAccount, PorterJob, ChannelJob


TAG = '[SCHEDULERS]'

# set small for debug
# INTERVAL_UNIT = 1
INTERVAL_UNIT = 60 # 1 minute

DOWNLOAD_JOB_INTERVAL = 5 * INTERVAL_UNIT
UPLOAD_JOB_INTERVAL = 4 * INTERVAL_UNIT
CHANNEL_JOB_INTERVAL = 60 * INTERVAL_UNIT
KUAIYINSHI_JOB_INTERVAL = 60 * INTERVAL_UNIT
RESET_QUOTA_JOB_INTERVAL = 12 * 60 * INTERVAL_UNIT

DELAY_INTERVAL = 0.1 * INTERVAL_UNIT
DELAY_START = 5 * INTERVAL_UNIT

YOUTUBE_UPLOAD_QUOTA = 90
YOUTUBE_UPLOAD_TIME_INTERVAL = 24 * 60 * INTERVAL_UNIT

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

download_job_lock = False
upload_job_lock = False

VIDEO_DESCRIPTION = """{}

This video is from (视频来源, 请支持原作者): {}

All videos are from online resources. If you find a video that infringes on your rights, please contact yportmaster@gmail.com to delete the video.
If you like this video, please like, comment and subscribe. Thank you!
(所有视频均来自网络资源, 如果侵犯了您的权益请联系yportmaster@gmail.com删除视频.
如果您喜欢此视频, 请点赞, 留言, 订阅. 非常感谢!)
"""

@scheduler.scheduled_job("interval", seconds=DOWNLOAD_JOB_INTERVAL, id='download')
def download_job():
    if not is_start_download_job():
        # print_log(TAG, 'Download job is stopped, skip this schedule...')
        return

    # find a job with account has quota
    job = None
    accounts = YoutubeAccount.objects.all()
    for account in accounts:
        pending_jobs = PorterJob.objects.filter(Q(status=PorterStatus.PENDING) &
                                                Q(youtube_account=account))
        for pending_job in pending_jobs:
            if pending_job.youtube_account.upload_quota > 0:
                job = pending_job
                break
        if job:
            break
    if not job:
        print_log(TAG, 'No pending download job available, skip this schedule...')
        return

    global download_job_lock

    if download_job_lock:
        print_log(TAG, 'Download job is still running, skip this schedule...')
        return

    print_log(TAG, 'Download job is started...')

    download_job_lock = True
    download(job)
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
        print_log(TAG, '*  Attention! Password may be required!  *')
        print_log(TAG, '******************************************')
        # upload to youtube
        upload_command = 'sudo youtube-upload --title="{}" --description="{}" --category="{}" --tags="{}" --client-secrets="{}" --credentials-file="{}"'.format(
            video.title,
            VIDEO_DESCRIPTION.format(video.description, video.url),
            video.category,
            video.print_tags(),
            youtube_account.secret_file,
            youtube_account.credentials_file
        )
        if job.playlist:
            upload_command = upload_command + ' --playlist="' + job.playlist + '"'
        upload_command = upload_command + ' ' + job.video_file
        # print_log(TAG, 'Run command: ' + upload_command)
        output = subprocess.check_output(upload_command, shell=True)
        youtube_id = output.decode("utf-8").strip()
        if 'Enter verification code: ' in youtube_id:
            youtube_id = youtube_id.replace('Enter verification code: ', '')
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
        # TODO, check exception upload limit or playlist limit
        # if playlist limit, upload status still should be true
        # update status to *UPLOAD_FAIL*
        job.status = PorterStatus.UPLOAD_FAIL
        job.save(update_fields=['status'])
        # set account quota 0 to avoid continue upload fail
        youtube_account.upload_quota = 0
        youtube_account.save(update_fields=['upload_quota'])
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
            # print_log(TAG, 'Create new job from channel fetch: ' + video_url)
            PorterJob(video_url=video_url, youtube_account=account).save()
        time.sleep(DELAY_INTERVAL)


@scheduler.scheduled_job("cron", hour=0, minute=30, id='bilibili_recommend', misfire_grace_time=60, coalesce=True)
def bilibili_recommend_job():
    if not is_start_bilibili_recommend_job():
        # print_log(TAG, 'Bilibili recommend job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Bilibili recommend job is started...')

    bilibili_recommend_fetch()


@scheduler.scheduled_job("interval", seconds=KUAIYINSHI_JOB_INTERVAL, id='kuaiyinshi_recommend')
def kuaiyinshi_recommend_job():
    if not is_start_kuaiyinshi_recommend_job():
        return

    print_log(TAG, 'Kuaiyinshi recommend job is started...')

    time.sleep(DELAY_START)
    douyin_recommend_fetch()


@scheduler.scheduled_job("interval", seconds=RESET_QUOTA_JOB_INTERVAL, id='reset_quota')
def reset_quota_job():
    if not is_start_reset_quota_job():
        # print_log(TAG, 'Reset quota job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Reset quota job is started...')
    accounts = YoutubeAccount.objects.all()
    for account in accounts:
        if account.upload_quota > 0:
            continue
        # OPTIMIZE, use last 99 job upload time
        last_success_job = account.porter_jobs.filter(status=PorterStatus.SUCCESS).reverse().first()
        should_reset = False
        if last_success_job:
            interval = get_current_time() - last_success_job.upload_at
            if interval.total_seconds() > YOUTUBE_UPLOAD_TIME_INTERVAL:
                should_reset = True
        else:
            should_reset = True
        if should_reset:
            account.upload_quota = YOUTUBE_UPLOAD_QUOTA
            account.save(update_fields=['upload_quota'])
            print_log(TAG, 'Reset quota for account: ' + account.name)


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
