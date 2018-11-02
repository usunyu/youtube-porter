import os, subprocess, requests, json, time
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Q
from porter.utils import *
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.fetchers.bilibili_fetcher import bilibili_channel_fetch, bilibili_recommend_fetch
from porter.downloaders.kuaiyinshi_downloader import douyin_download
from porter.enums import VideoSource, PorterStatus
from porter.models import Video, YoutubeAccount, PorterJob, ChannelJob


TAG = '[SCHEDULERS]'

# set small for debug
# INTERVAL_UNIT = 1
INTERVAL_UNIT = 60 # 1 minute

DOWNLOAD_JOB_INTERVAL = 5 * INTERVAL_UNIT
UPLOAD_JOB_INTERVAL = 4 * INTERVAL_UNIT
CHANNEL_JOB_INTERVAL = 60 * INTERVAL_UNIT
RESET_QUOTA_JOB_INTERVAL = 30 * INTERVAL_UNIT

DELAY_INTERVAL = 0.1 * INTERVAL_UNIT

YOUTUBE_UPLOAD_QUOTA = 90
YOUTUBE_UPLOAD_TIME_INTERVAL = 24 * 60 * INTERVAL_UNIT

RETRY_LIMIT = 3

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
        download_ret = bilibili_download(job)
    elif job.video_source == VideoSource.DOUYIN:
        download_ret = douyin_download(job)
    else:
        download_ret = [PorterStatus.DOWNLOAD_FAIL, None]

    status = download_ret[0]

    # download video success
    if status == PorterStatus.DOWNLOADED:
        video_file = download_ret[1]
        # update job video file
        job.video_file = video_file
        job.download_at = get_current_time()
        job.save(update_fields=['video_file', 'download_at'])

    # download video failed, check retry
    if status == PorterStatus.DOWNLOAD_FAIL or status == PorterStatus.API_EXCEPTION:
        job.retried = job.retried + 1
        job.save(update_fields=['retried'])
        if job.retried < RETRY_LIMIT:
            # reset status to *PENDING*
            status = PorterStatus.PENDING

    # update status to corresponding status
    job.status = status
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
        time.sleep(DELAY_INTERVAL)


@scheduler.scheduled_job("cron", hour=0, minute=30, id='bilibili_recommend', misfire_grace_time=60, coalesce=True)
def bilibili_recommend_job():
    if not is_start_bilibili_recommend_job():
        # print_log(TAG, 'Bilibili recommend job is stopped, skip this schedule...')
        return

    print_log(TAG, 'Bilibili recommend job is started...')

    bilibili_recommend_fetch()


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
            # TODO, see https://github.com/usunyu/youtube-porter/issues/49
            if account.name == 'yportdance':
                account.upload_quota = 20
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
