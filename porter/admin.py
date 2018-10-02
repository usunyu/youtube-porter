from django.contrib import admin
from porter.models import *

admin.site.register(YoutubeAccount)
admin.site.register(VideoTag)
admin.site.register(Video)

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
