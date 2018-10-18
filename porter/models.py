from django.db import models
from porter.enums import PorterStatus, VideoSource, PorterJobType


class YoutubeAccount(models.Model):
    name = models.CharField(max_length=256)
    secret_file = models.CharField(max_length=256)
    upload_quota = models.PositiveSmallIntegerField(default=0)
    channel = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VideoTag(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Video(models.Model):
    url = models.CharField(max_length=256)
    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    tags = models.ManyToManyField(VideoTag, related_name='videos')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        return '-'

    def print_tags(self):
        if self.tags.count() == 0:
            return 'entertainment'
        return ', '.join([tag.name for tag in self.tags.all()])


class ChannelJob(models.Model):
    url = models.CharField(max_length=256)
    name = models.CharField(max_length=256, null=True, blank=True)
    VIDEO_SOURCE_CHOICES = (
        (VideoSource.BILIBILI, VideoSource.tostr(VideoSource.BILIBILI)),
        (VideoSource.YOUKU, VideoSource.tostr(VideoSource.YOUKU))
    )
    video_source = models.PositiveSmallIntegerField(
        choices=VIDEO_SOURCE_CHOICES,
        default=VideoSource.BILIBILI
    )
    youtube_account = models.ForeignKey(
        YoutubeAccount,
        on_delete=models.SET_NULL,
        related_name='channel_jobs',
        null=True,
        blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    last_fetched_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        return '-'


class PorterJob(models.Model):
    video_url = models.CharField(max_length=256)
    VIDEO_SOURCE_CHOICES = (
        (VideoSource.BILIBILI, VideoSource.tostr(VideoSource.BILIBILI)),
        (VideoSource.YOUKU, VideoSource.tostr(VideoSource.YOUKU))
    )
    video_source = models.PositiveSmallIntegerField(
        choices=VIDEO_SOURCE_CHOICES,
        default=VideoSource.BILIBILI
    )
    youtube_account = models.ForeignKey(
        YoutubeAccount,
        on_delete=models.SET_NULL,
        related_name='porter_jobs',
        null=True,
        blank=True)
    youtube_id = models.CharField(
        max_length=32,
        null=True,
        blank=True)
    playlist = models.CharField(
        max_length=256,
        null=True,
        blank=True)
    video = models.OneToOneField(
        Video,
        on_delete=models.SET_NULL,
        related_name='porter_job',
        null=True,
        blank=True
    )
    video_file = models.CharField(max_length=64, null=True, blank=True)
    PORTER_STATUS_CHOICES = (
        (PorterStatus.PENDING, PorterStatus.tostr(PorterStatus.PENDING)),
        (PorterStatus.DOWNLOADING, PorterStatus.tostr(PorterStatus.DOWNLOADING)),
        (PorterStatus.DOWNLOADED, PorterStatus.tostr(PorterStatus.DOWNLOADED)),
        (PorterStatus.UPLOADING, PorterStatus.tostr(PorterStatus.UPLOADING)),
        (PorterStatus.SUCCESS, PorterStatus.tostr(PorterStatus.SUCCESS)),
        (PorterStatus.DOWNLOAD_FAIL, PorterStatus.tostr(PorterStatus.DOWNLOAD_FAIL)),
        (PorterStatus.UPLOAD_FAIL, PorterStatus.tostr(PorterStatus.UPLOAD_FAIL)),
        (PorterStatus.DUPLICATED, PorterStatus.tostr(PorterStatus.DUPLICATED)),
    )
    status = models.PositiveSmallIntegerField(
        choices=PORTER_STATUS_CHOICES,
        default=PorterStatus.PENDING
    )
    PORTER_JOB_TYPE_CHOICES = (
        (PorterJobType.COMPLETE, PorterJobType.tostr(PorterJobType.COMPLETE)),
        (PorterJobType.PARTIAL, PorterJobType.tostr(PorterJobType.PARTIAL)),
    )
    type = models.PositiveSmallIntegerField(
        choices=PORTER_JOB_TYPE_CHOICES,
        default=PorterJobType.COMPLETE
    )
    part = models.PositiveSmallIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    download_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    upload_at = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    def __str__(self):
        return self.video_url


class Settings(models.Model):
    start_download_job = models.BooleanField(default=False)
    start_upload_job = models.BooleanField(default=False)
    start_channel_job = models.BooleanField(default=False)
    start_bilibili_recommend_job = models.BooleanField(default=False)
    start_reset_quota_job = models.BooleanField(default=False)
