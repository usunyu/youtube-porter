import logging, os, subprocess, random, string
import logging.handlers
from PIL import Image
from django.utils import timezone
from django.db.models import Q
from ipaddress import ip_address
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

IP_ADDR = None

def print_log(tag, msg):
    dt = timezone.localtime(timezone.now())
    print(tag, dt.strftime('%Y-%m-%d %H:%M:%S'), msg)
    logger.debug(msg)


def print_exception(tag, msg):
    dt = timezone.localtime(timezone.now())
    print(tag, dt.strftime('%Y-%m-%d %H:%M:%S'), msg)
    logger.exception(msg)


def set_ip_addr(ip):
    global IP_ADDR
    IP_ADDR = ip

def prepare_ip():
    global IP_ADDR
    if IP_ADDR:
        return
    rip = ip_address('0.0.0.0')
    while rip.is_private:
        rip = ip_address('.'.join(map(str, (random.randint(0, 255) for _ in range(4)))))
    IP_ADDR = rip


def get_browser_headers():
    return {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}


def get_douyin_headers():
    prepare_ip()
    return {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'accept-encoding': 'gzip, deflate, br',
		'accept-language': 'zh-CN,zh;q=0.9',
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
		'upgrade-insecure-requests': '1',
		'user-agent': 'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; MI 4S Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.146 Mobile Safari/537.36 XiaoMi/MiuiBrowser/9.1.3',
		'X-Real-IP': str(IP_ADDR),
		'X-Forwarded-For': str(IP_ADDR),
    }


def get_current_time():
    return timezone.now()


def get_random_code(count):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(count))


def get_random_16_code():
    return get_random_code(16)


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


def is_start_kuaiyinshi_merge_job():
    settings = Settings.objects.all().first()
    if not settings:
        return False
    return settings.start_kuaiyinshi_merge_job


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


def get_youtube_test_account():
    account = YoutubeAccount.objects.filter(name='usunyu').first()
    return account


def get_youtube_yportmaster_account():
    account = YoutubeAccount.objects.filter(name='yportmaster').first()
    return account


def get_youtube_yporttiktok_account():
    account = YoutubeAccount.objects.filter(name='yporttiktok').first()
    return account


def get_youtube_yportcomment_account():
    account = YoutubeAccount.objects.filter(name='yportcomment').first()
    return account


def find_youtube_job_has_quota(status):
    job = None
    # get job by priority
    priority_jobs = PorterJob.objects.filter(Q(status=status) &
                                             Q(priority=True))
    for priority_job in priority_jobs:
        if priority_job.youtube_account.upload_quota > 0:
            job = priority_job
        if job:
            break

    if job:
        return job

    # get job by account order
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


def clean_file(tag, file):
    if not os.path.exists(file):
        return
    try:
        os.remove(file)
        print_log(tag, 'Deleted file: ' + file)
    except:
        print_exception(tag, 'Delete file: ' + file + ' exception!')


def merge_images(images, target, clean=True):
    tag = '[MERGE IMAGES]'
    imagefiles = []
    total_width = 0
    max_height = 0
    widths = []
    heights = []
    for image in images:
        imagefile = Image.open(image)
        imagefiles.append(imagefile)
        total_width = total_width + imagefile.width
        widths.append(imagefile.width)
        heights.append(imagefile.height)
        if imagefile.height > max_height:
            max_height = imagefile.height
    targetfile = Image.new('RGB', (total_width, max_height))
    left = 0
    for i in range(0, len(imagefiles)):
        image = imagefiles[i]
        right = widths[i]
        targetfile.paste(image, (left, 0))
        left += widths[i]
        right = left + widths[i]
        targetfile.save(target, quality=100)
    if clean:
        for image in images:
            clean_file(tag, image)


def resize_video(video, width, height, target, clean=True):
    tag = '[RESIZE VIDEO]'
    print_log(tag, 'Resizing video {}...'.format(video))
    command = 'ffmpeg -i {} -vf "scale={}:{}:force_original_aspect_ratio=decrease,pad={}:{}:(ow-iw)/2:(oh-ih)/2" {}'.format(
        video,
        width, height,
        width, height,
        target)
    subprocess.run([command], shell=True)
    if clean:
        clean_file(tag, video)


def merge_videos(videos, target, clean=True):
    tag = '[MERGE VIDEOS]'
    concat_params = ''
    # re-encode videos
    for i in range(0, len(videos)):
        video = videos[i]
        temp_file = 'tempvideo' + str(i) + '.mpg'
        print_log(tag, 'Merging video {}/{}'.format(i + 1, len(videos)))
        subprocess.run(['ffmpeg -i {} -qscale:v 1 {}'.format(video, temp_file)], shell=True)
        # delete origin files
        if clean:
            clean_file(tag, video)
        if concat_params:
            concat_params = concat_params + '|' + temp_file
        else:
            concat_params = temp_file
    # merge videos
    subprocess.run(['ffmpeg -i concat:"{}" -c copy temptarget.mpg'.format(concat_params)], shell=True)
    # re-encode to origin format
    subprocess.run(['ffmpeg -i temptarget.mpg -qscale:v 2 {}'.format(target)], shell=True)
    # clean files
    if clean:
        for i in range(0, len(videos)):
            temp_file = 'tempvideo' + str(i) + '.mpg'
            clean_file(tag, temp_file)
        clean_file(tag, 'temptarget.mpg')


def get_video_job_score(job):
    return 4 * job.shares + 3 * job.comments + 2 * job.likes + job.views


def get_video_duration(video_file):
    command = 'ffprobe -v quiet -of csv=p=0 -show_entries format=duration "{}"'.format(video_file)
    output = subprocess.check_output(command, shell=True)
    duration = int(output.decode('utf-8').strip().split('.')[0])
    return duration


# Account Settings

def get_no_playlist_accounts():
    return [
        # 'yportshort',
        'potatosixdao',
        'cailaobanwork',
        'renrenvideotv',
        'flowerdirtyprpr',
        'jushuoshow',
        'tenminutesmovie',
    ]


def get_no_copyright_desc_accounts():
    return [
        'potatosixdao',
        'cailaobanwork',
        'jushuoshow',
        'flowerdirtyprpr',
        'renrenvideotv',
    ]


def get_youtube_quota_settings():
    return {
        'yportmaster': 20,
        'yportdance': 5,
        'yportgame': 5,
        # 'yportcomment': 0,
        # 'yportshort': 0,
        'yportkitty': 1,
        'potatosixdao': 20,
        'cailaobanwork': 20,
        'renrenvideotv': 30,
        'flowerdirtyprpr': 1,
        'jushuoshow': 1,
        'tenminutesmovie': 5,
    }


def get_youtube_account_order():
    return [
        # 'yportcomment',
        'tenminutesmovie',
        'potatosixdao',
        'jushuoshow',
        'flowerdirtyprpr',
        'cailaobanwork',
        'renrenvideotv',
        'yportdance',
        'yportkitty',
        'yportmaster',
        'yportgame',
        'usunyu',
    ]
