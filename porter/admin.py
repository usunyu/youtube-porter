from django.contrib import admin
from porter.models import *

admin.site.register(YoutubeAccount)
admin.site.register(VideoTag)

class VideoAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'url',
        'api_url',
        'title',
        'description',
        'all_tags'
    ]

    def all_tags(self, obj):
        return ', '.join([tag.name for tag in obj.tags.all()])

admin.site.register(Video, VideoAdmin)

class PorterJobAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'video_url',
        'video_source',
        'video',
        'video_file',
        'youtube_account',
        'status'
    ]

    readonly_fields = ['video', 'video_file', 'status']

admin.site.register(PorterJob, PorterJobAdmin)
