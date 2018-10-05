from django.db import models
from porter.enums import PorterStatus, VideoSource


class YoutubeAccount(models.Model):
    name = models.CharField(max_length=256)
    secret_file = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class VideoTag(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64)

    def __str__(self):
        return self.name


class Video(models.Model):
    # TODO add created time
    url = models.CharField(max_length=256)
    api_url = models.CharField(max_length=256, null=True, blank=True)
    title = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    tags = models.ManyToManyField(VideoTag, related_name='videos')

    def __str__(self):
        if self.title:
            return self.title
        return 'None'

    def print_tags(self):
        return ', '.join([tag.name for tag in self.tags.all()])


class PorterJob(models.Model):
    # TODO add download time, upload time
    video_url = models.CharField(max_length=256)
    VIDEO_SOURCE_CHOICES = (
        (VideoSource.BILIBILI, 'Bilibili'),
        (VideoSource.YOUKU, 'Youku')
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
    video = models.OneToOneField(
        Video,
        on_delete=models.SET_NULL,
        related_name='porter_job',
        null=True,
        blank=True
    )
    video_file = models.CharField(max_length=64, null=True, blank=True)
    PORTER_STATUS_CHOICES = (
        (PorterStatus.PENDING, 'Pending'),
        (PorterStatus.DOWNLOADING, 'Downloading'),
        (PorterStatus.DOWNLOADED, 'Downloaded'),
        (PorterStatus.UPLOADING, 'Uploading'),
        (PorterStatus.SUCCESS, 'Success'),
        (PorterStatus.DOWNLOAD_FAIL, 'Download Fail'),
        (PorterStatus.UPLOAD_FAIL, 'Upload Fail'),
        (PorterStatus.DUPLICATED, 'Duplicated'),
    )
    status = models.PositiveSmallIntegerField(
        choices=PORTER_STATUS_CHOICES,
        default=PorterStatus.PENDING
    )

    def __str__(self):
        return self.video_url
