from enum import Enum

class VideoSource(Enum):
    BILIBILI = 'Bilibili'
    YOUKU = 'Youku'

class PorterStatus(Enum):
    PENDING = 'Pending'
    DOWNLOADING = 'Downloading'
    UPLOADING = 'Uploading'
    SUCCESS = 'Success'
