import logging
import logging.handlers
from django.utils import timezone
from porter.models import Settings


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


def is_start_bilibili_recommend_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_bilibili_recommend_job


def get_youtube_invalid_content_chars():
    return [
        '<',
        '>',
        '"',
        '`',
        "'",
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
    ]
