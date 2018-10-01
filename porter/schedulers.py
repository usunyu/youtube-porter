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

job_lock = False

@scheduler.scheduled_job("interval", seconds=JOB_INTERVAL, id='porter')
def porter_job():
    global job_lock
    if job_lock:
        print_log(TAG, 'Job is still running, skip this schedule...')
        return
    job_lock = True
    jobs = PorterJob.objects.filter(status=PorterStatus.PENDING)
    for job in jobs:
        print_log(TAG, 'Start to run job: ' + str(job.id))
        print_log(TAG, 'Video url: ' + job.video_url)
        print_log(TAG, 'Video source: ' + VideoSource.tostr(job.video_source))
        print_log(TAG, 'Youtube account: ' + job.youtube_account.name)

        if job.video_source == VideoSource.BILIBILI:
            bilibili_download(job.video_url)
        else:
            pass

    job_lock = False


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
