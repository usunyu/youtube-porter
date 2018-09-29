from django.db import models


class Video(models.Model):
    title = models.CharField(null=False, max_length=256)
    description = models.TextField(null=True, blank=True)
    tags = models.ManyToManyField(VideoTag, related_name='videos')

    def __str__(self):
        return u'Video: {}'.format(self.title)


class VideoTag(models.Model):
    name = models.CharField(unique=True, null=False, db_index=True, max_length=64)

    def __str__(self):
        return u'VideoTag: {}'.format(self.name)
