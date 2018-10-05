import os, subprocess
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.models import Q
from porter.utils import print_log, get_current_time
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.enums import VideoSource, PorterStatus
from porter.models import Video, PorterJob


TAG = '[SCHEDULERS]'
# for debug
JOB_INTERVAL = 10
# JOB_INTERVAL = 60 * 10

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

download_job_lock = False
upload_job_lock = False

@scheduler.scheduled_job("interval", seconds=JOB_INTERVAL, id='download')
def download_job():
    global download_job_lock
    if download_job_lock:
        print_log(TAG, 'Download job is still running, skip this schedule...')
        return
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

    download_job_lock = False


@scheduler.scheduled_job("interval", seconds=JOB_INTERVAL, id='upload')
def upload_job():
    global upload_job_lock
    if upload_job_lock:
        print_log(TAG, 'Upload job is still running, skip this schedule...')
        return
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
                    video.description,
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

    upload_job_lock = False


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
