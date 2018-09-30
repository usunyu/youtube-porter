from django.db import models
from porter.enums import PorterStatus, VideoSource


class YoutubeAccount(models.Model):
    name = models.CharField(max_length=256)
    secret_file = models.CharField(max_length=256)

    def __str__(self):
        return u'YoutubeAccount: {}'.format(self.name)


class VideoTag(models.Model):
    name = models.CharField(unique=True, db_index=True, max_length=64)

    def __str__(self):
        return u'VideoTag: {}'.format(self.name)


class Video(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(VideoTag, related_name='videos')

    def __str__(self):
        return u'Video: {}'.format(self.title)


class PorterJob(models.Model):
    video_url = models.CharField(max_length=256)
    video_source = models.CharField(
        max_length=32,
        choices=[(source, source.value) for source in VideoSource],
        default=VideoSource.BILIBILI
    )
    youtube_account = models.ForeignKey(
        YoutubeAccount,
        on_delete=models.CASCADE,
        related_name='porter_jobs')
    status = models.CharField(
        max_length=32,
        choices=[(status, status.value) for status in PorterStatus],
        default=PorterStatus.PENDING
    )

    def __str__(self):
        return u'PorterJob: {}'.format(self.video_url)
