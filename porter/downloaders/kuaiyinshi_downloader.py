from porter.utils import *
from porter.enums import PorterStatus
from porter.downloaders.url_downloader import url_download

TAG = '[KUAIYINSHI DOWNLOADER]'


def download(job, source):
    file = url_download(job.download_url)
    duration = get_video_duration(file)
    # update video duration
    video = job.video
    video.duration = duration
    video.save(update_fields=['duration'])
    print_log(TAG, 'Downloaded {} video {}'.format(source, file))
    return PorterStatus.PENDING_MERGE

def douyin_download(job):
    return download(job, 'DouYin')

def meipai_download(job):
    return download(job, 'MeiPai')

def kuaishou_download(job):
    return download(job, 'KuaiShou')

def huoshan_download(job):
    return download(job, 'HuoShan')
