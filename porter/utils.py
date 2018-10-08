import logging
import logging.handlers
from django.utils import timezone


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
