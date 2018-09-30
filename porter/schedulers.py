from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from porter.models import PorterJob


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), 'default')

TAG = '[SCHEDULERS]'

def print_log(msg):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    # bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    us_dt = utc_dt.astimezone(timezone(timedelta(hours=-7)))
    print(TAG, us_dt.strftime("%Y-%m-%d %H:%M:%S"), msg)


@scheduler.scheduled_job("interval", seconds=60, id='porter')
def porter_job():

    print_log('Run schedule job now.')


# avoid multi-thread to start multiple schedule jobs
import fcntl
try:
    lock = open('lock.obj', 'w+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    print_log('Schedule job started!')
    register_events(scheduler)
    scheduler.start()
except IOError as e:
    print_log('Schedule job already start, skip...')
