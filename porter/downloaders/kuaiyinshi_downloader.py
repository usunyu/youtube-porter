import requests, json, re, os, subprocess
from requests_html import HTMLSession
from porter.utils import *
from porter.models import VideoTag, PorterJob
from porter.enums import VideoSource, PorterStatus, PorterJobType
from porter.downloaders.url_downloader import url_download

TAG = '[DOUYIN DOWNLOADER]'


def douyin_download(job):
    # TODO

    print_log(TAG, 'Fetch data error!')
    return [PorterStatus.API_ERROR, None]
