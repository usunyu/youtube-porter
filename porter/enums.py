class VideoSource:
    BILIBILI = 0
    YOUKU = 1

    @staticmethod
    def tostr(val):
        if val == VideoSource.BILIBILI:
            return 'Bilibili'
        if val == VideoSource.YOUKU:
            return 'Youku'
        return 'Unknown'

class PorterStatus:
    PENDING = 0
    DOWNLOADING = 1
    UPLOADING = 2
    SUCCESS = 3

    @staticmethod
    def tostr(val):
        if val == PorterStatus.PENDING:
            return 'Pending'
        if val == PorterStatus.DOWNLOADING:
            return 'Downloading'
        if val == PorterStatus.UPLOADING:
            return 'Uploading'
        if val == PorterStatus.SUCCESS:
            return 'Success'
        return 'Unknown'
