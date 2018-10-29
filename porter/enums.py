UNKNOWN = 'Unknown'

class VideoSource:
    BILIBILI = 0
    YOUKU = 1 # TODO
    IQIYI = 2 # TODO
    DOUYIN = 3 # TODO
    MEIPAI = 4 # TODO
    KUAISHOU = 5 # TODO
    HUOSHAN = 6 # TODO

    @staticmethod
    def tostr(val):
        if val == VideoSource.BILIBILI:
            return '哔哩哔哩'
        if val == VideoSource.YOUKU:
            return '优酷'
        if val == VideoSource.IQIYI:
            return '爱奇艺'
        if val == VideoSource.DOUYIN:
            return '抖音'
        if val == VideoSource.MEIPAI:
            return '美拍'
        if val == VideoSource.KUAISHOU:
            return '快手'
        if val == VideoSource.HUOSHAN:
            return '火山'
        return UNKNOWN

class PorterStatus:
    # video is pending for download
    PENDING = 0
    # video is downloading
    DOWNLOADING = 1
    # video is downloaded
    DOWNLOADED = 2
    # video is uploading
    UPLOADING = 3
    # video is download & upload success
    SUCCESS = 4
    # video is download failed
    DOWNLOAD_FAIL = 5
    # video is upload failed
    UPLOAD_FAIL = 6
    # video is duplicated with other one
    DUPLICATED = 7
    # error during api request
    API_ERROR = 8
    # video is not found or deleted
    VIDEO_NOT_FOUND = 9
    # created new jobs for multi part
    PARTIAL = 10
    # video is pending for merge
    PENDING_MERGE = 11
    # video is merged
    MERGED = 12
    # exception during api request
    API_EXCEPTION = 13

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
        if val == PorterStatus.API_ERROR:
            return 'API Error'
        if val == PorterStatus.VIDEO_NOT_FOUND:
            return 'Video Not Found'
        if val == PorterStatus.PARTIAL:
            return 'Partial'
        if val == PorterStatus.PENDING_MERGE:
            return 'Pending Merge'
        if val == PorterStatus.MERGED:
            return 'Merged'
        if val == PorterStatus.API_EXCEPTION:
            return 'API Exception'
        return UNKNOWN

class PorterJobType:
    COMPLETE = 0
    PARTIAL = 1
    MERGE = 2

    @staticmethod
    def tostr(val):
        if val == PorterJobType.COMPLETE:
            return 'Complete'
        if val == PorterJobType.PARTIAL:
            return 'Partial'
        if val == PorterJobType.MERGE:
            return 'Merge'
        return UNKNOWN
