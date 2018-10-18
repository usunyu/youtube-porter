UNKNOWN = 'Unknown'

class VideoSource:
    BILIBILI = 0
    YOUKU = 1

    @staticmethod
    def tostr(val):
        if val == VideoSource.BILIBILI:
            return 'Bilibili'
        if val == VideoSource.YOUKU:
            return 'Youku'
        return UNKNOWN

class PorterStatus:
    PENDING = 0
    DOWNLOADING = 1
    DOWNLOADED = 2
    UPLOADING = 3
    SUCCESS = 4
    DOWNLOAD_FAIL = 5
    UPLOAD_FAIL = 6
    DUPLICATED = 7

    @staticmethod
    def tostr(val):
        if val == PorterStatus.PENDING:
            return 'Pending'
        if val == PorterStatus.DOWNLOADING:
            return 'Downloading'
        if val == PorterStatus.DOWNLOADED:
            return 'Downloaded'
        if val == PorterStatus.UPLOADING:
            return 'Uploading'
        if val == PorterStatus.SUCCESS:
            return 'Success'
        if val == PorterStatus.DOWNLOAD_FAIL:
            return 'Download Fail'
        if val == PorterStatus.UPLOAD_FAIL:
            return 'Upload Fail'
        if val == PorterStatus.DUPLICATED:
            return 'Duplicated'
        return UNKNOWN

class PorterJobType:
    COMPLETE = 0
    PARTIAL = 1

    @staticmethod
    def tostr(val):
        if val == PorterJobType.COMPLETE:
            return 'Complete'
        if val == PorterJobType.PARTIAL:
            return 'Partial'
        return UNKNOWN
