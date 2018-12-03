from porter.utils import *
from porter.enums import PorterStatus, VideoSource
from porter.downloaders.url_downloader import url_download

TAG = '[KUAIYINSHI DOWNLOADER]'


def download(job, source):
    headers = get_browser_headers()
    download_url = job.download_url
    if source == VideoSource.DOUYIN:
        headers = get_douyin_headers()
        # use no watermark video link
        download_url = download_url.replace('/playwm/', '/play/')

    file = url_download(download_url, headers)
    # update video file
    job.video_file = file
    job.save(update_fields=['video_file'])
    duration = get_video_duration(file)
    # update video duration
    video = job.video
    video.duration = duration
    video.save(update_fields=['duration'])
    print_log(TAG, 'Downloaded video from {}, {}'.format(VideoSource.tostr(source), file))
    return PorterStatus.PENDING_MERGE

def douyin_download(job):
    return download(job, VideoSource.DOUYIN)

def meipai_download(job):
    return download(job, VideoSource.MEIPAI)

def kuaishou_download(job):
    return download(job, VideoSource.KUAISHOU)

def huoshan_download(job):
    return download(job, VideoSource.HUOSHAN)
