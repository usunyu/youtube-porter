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
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(VideoTag, related_name='videos')

    def __str__(self):
        return self.title


class PorterJob(models.Model):
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
        on_delete=models.CASCADE,
        related_name='porter_jobs')
    PORTER_STATUS_CHOICES = (
        (PorterStatus.PENDING, 'Pending'),
        (PorterStatus.DOWNLOADING, 'Downloading'),
        (PorterStatus.UPLOADING, 'Uploading'),
        (PorterStatus.SUCCESS, 'Success')
    )
    status = models.PositiveSmallIntegerField(
        choices=PORTER_STATUS_CHOICES,
        default=PorterStatus.PENDING
    )

    def __str__(self):
        return self.video_url
