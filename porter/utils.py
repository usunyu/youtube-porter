import logging, os
import logging.handlers
from django.utils import timezone
from django.db.models import Q
from porter.enums import PorterStatus
from porter.models import PorterJob, YoutubeAccount, Settings


LOG_FILE = 'debug.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5)
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger('debug')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def print_log(tag, msg):
    dt = timezone.localtime(timezone.now())
    print(tag, dt.strftime('%Y-%m-%d %H:%M:%S'), msg)
    logger.debug(msg)


def print_exception(tag, msg):
    dt = timezone.localtime(timezone.now())
    print(tag, dt.strftime('%Y-%m-%d %H:%M:%S'), msg)
    logger.exception(msg)


def get_client_headers():
    return {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}


def get_current_time():
    return timezone.now()


def get_time_str():
    dt = timezone.localtime(timezone.now())
    return dt.strftime('%Y-%m-%d %H-%M-%S')


def is_start_download_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_download_job


def is_start_upload_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_upload_job


def is_start_channel_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_channel_job


def is_start_bilibili_recommend_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_bilibili_recommend_job


def is_start_kuaiyinshi_recommend_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_kuaiyinshi_recommend_job


def is_start_reset_quota_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_reset_quota_job


def get_youtube_invalid_content_chars():
    return [
        '<',
        '>',
        '"',
        '`',
        "'",
        '\\',
    ]


def get_youtube_invalid_tag_chars():
    return [
        '<',
        '>',
        ',',
        '，',
        '"',
        '`',
        "'",
        "\\",
    ]


def find_youtube_job_has_quota(status):
    job = None
    account_order = get_youtube_account_order()
    for account_name in account_order:
        account = YoutubeAccount.objects.filter(name=account_name).first()
        if not account:
            continue

        available_jobs = PorterJob.objects.filter(Q(status=status) &
                                                  Q(youtube_account=account))
        for available_job in available_jobs:
            # find a job with account has quota
            if available_job.youtube_account.upload_quota > 0:
                job = available_job
                break
        if job:
            break

    return job


def get_no_playlist_accounts():
    return ['yportshort']


def get_youtube_quota_settings():
    return {
        'yportmaster': 5,
        'yportdance': 5,
        'yportgame': 5,
        'yportcomment': 10,
        'yportshort': 0
    }


def get_youtube_account_order():
    return [
        'yportcomment',
        'yportdance',
        'yportmaster',
        'yportgame',
    ]


def clean_file(TAG, file):
    if not os.path.exists(file):
        return
    try:
        os.remove(file)
        print_log(TAG, 'Deleted file: ' + file)
    except:
        print_exception(TAG, 'Delete file: ' + file + ' exception!')
