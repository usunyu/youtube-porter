import os, subprocess, requests, json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Q
from porter.utils import print_log, get_current_time
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.enums import VideoSource, PorterStatus
from porter.models import Video, PorterJob, YoutubeAccount


TAG = '[SCHEDULERS]'
# set small for debug
# JOB_INTERVAL = 10
JOB_INTERVAL = 60 * 10

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

download_job_lock = False
upload_job_lock = False

VIDEO_DESCRIPTION = """所有视频均来自网络资源, 如果侵犯了您的权益请联系yportmaster@gmail.com删除视频.
如果您喜欢此视频, 请点赞, 留言, 订阅. 非常感谢!


All videos are from online resources. If you find a video that infringes on your rights, please contact yportmaster@gmail.com to delete the video.
If you like this video, please like, comment and subscribe. Thank you!

This video is from: {}


{}
"""

@scheduler.scheduled_job("interval", seconds=JOB_INTERVAL, id='download')
def download_job():
    global download_job_lock
    if download_job_lock:
        print_log(TAG, 'Download job is still running, skip this schedule...')
        return
    try:
        download_job_lock = True
        jobs = PorterJob.objects.filter(status=PorterStatus.PENDING)
        for job in jobs:
            print_log(TAG, 'Start to download job: ' + str(job.id))
            print_log(TAG, 'Video url: ' + job.video_url)
            print_log(TAG, 'Video source: ' + VideoSource.tostr(job.video_source))
            print_log(TAG, 'Youtube account: ' + job.youtube_account.name)

            # check if job is duplicated
            if PorterJob.objects.filter(
                Q(video_url=job.video_url) &
                Q(youtube_account=job.youtube_account) &
                Q(status=PorterStatus.SUCCESS)
            ).exists():
                # update status to *DUPLICATED*
                job.status = PorterStatus.DUPLICATED
                job.save(update_fields=['status'])
                continue

            # create video object
            video = Video(
                url=job.video_url,
                category='Entertainment' # default to entertainment category
            )
            video.save()
            job.video = video
            # update status to *DOWNLOADING*
            job.status = PorterStatus.DOWNLOADING
            job.save(update_fields=['video', 'status'])
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
    except Exception as e:
        print_log(TAG, 'Unknown error happened in download job!')
        print(e)


    download_job_lock = False


@scheduler.scheduled_job("interval", seconds=JOB_INTERVAL, id='upload')
def upload_job():
    global upload_job_lock
    if upload_job_lock:
        print_log(TAG, 'Upload job is still running, skip this schedule...')
        return
    try:
        upload_job_lock = True
        jobs = PorterJob.objects.filter(status=PorterStatus.DOWNLOADED)
        for job in jobs:
            video = job.video
            print_log(TAG, 'Start to upload job: ' + str(job.id))
            print_log(TAG, 'Video: ' + video.title)
            print_log(TAG, 'Youtube account: ' + job.youtube_account.name)
            try:
                # update status to *UPLOADING*
                job.status = PorterStatus.UPLOADING
                job.save(update_fields=['status'])
                print_log(TAG, '****** You may need input password! ******')
                # upload to youtube
                output = subprocess.check_output(
                    'sudo youtube-upload --title="{}" --description="{}" --category="{}" --tags="{}" --client-secrets="{}" "{}"'.format(
                        video.title,
                        VIDEO_DESCRIPTION.format(video.url, video.description),
                        video.category,
                        video.print_tags(),
                        job.youtube_account.secret_file,
                        job.video_file
                    ),
                    shell=True
                )
                youtube_id = output.decode("utf-8").strip()
                job.youtube_id = youtube_id
                job.upload_at = get_current_time()
                # update status to *SUCCESS*
                job.status = PorterStatus.SUCCESS
                job.save(update_fields=['youtube_id', 'status', 'upload_at'])

            except Exception as e:
                print_log(TAG, 'Failed to upload video: ' + video.title)
                print(e)
                # update status to *UPLOAD_FAIL*
                job.status = PorterStatus.UPLOAD_FAIL
                job.save(update_fields=['status'])
            # clean video file
            try:
                os.remove(job.video_file)
                print_log(TAG, 'Deleted video: ' + job.video_file)
            except Exception as e:
                print_log(TAG, 'Failed to delete video: ' + job.video_file)
                print(e)
    except Exception as e:
        print_log(TAG, 'Unknown error happened in upload job!')
        print(e)

    upload_job_lock = False


@scheduler.scheduled_job("cron", hour=0, minute=0, id='bilibili_recommend', misfire_grace_time=60, coalesce=True)
def bilibili_recommend_job():
    try:
        response = requests.get('http://api.bilibili.cn/recommend')
        list = json.loads(response.text)['list']

        account = YoutubeAccount.objects.all().first()

        for record in list:
            aid = record['aid']
            # create porter job
            video_url = '{}{}'.format('https://www.bilibili.com/video/av', aid)
            if PorterJob.objects.filter(
                Q(video_url=video_url) &
                Q(youtube_account=account)
            ).exists():
                continue
            print_log(TAG, 'Create new job from bilibili recommend api: ' + video_url)
            PorterJob(video_url=video_url, youtube_account=account).save()
    except Exception as e:
        print_log(TAG, 'Unknown error happened in bilibili_recommend job!')
        print(e)

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
