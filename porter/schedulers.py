from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from porter.utils import print_log
from porter.downloaders.bilibili_downloader import bilibili_download
from porter.enums import VideoSource, PorterStatus
from porter.models import PorterJob


TAG = '[SCHEDULERS]'
JOB_INTERVAL = 300

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

        if PorterJob.objects.filter(video_url=job.video_url).exists():
            print_log(TAG, 'Youtube account: ' + job.youtube_account.name)

        # update status to *DOWNLOADING*
        job.status = PorterStatus.DOWNLOADING
        job.save(update_fields=['status'])
        # download the video
        if job.video_source == VideoSource.BILIBILI:
            video_file = bilibili_download(job.video_url)
        else:
            video_file = None

        if video_file:
            # create video object
            video = Video(url=job.video_url)
            video.save()
            # update job video
            job.video = video
            # update status to *DOWNLOADED*
            job.status = PorterStatus.DOWNLOADED
            job.save(update_fields=['video', 'status'])
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
        print_log(TAG, 'Start to upload job: ' + str(job.id))
        # print_log(TAG, 'Video: ' + job.video.title)
        print_log(TAG, 'Youtube account: ' + job.youtube_account.name)
        # TODO

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
