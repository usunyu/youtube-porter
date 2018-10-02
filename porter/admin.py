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
        'youtube_account',
        'status'
    ]

    readonly_fields = ['video', 'status']

admin.site.register(PorterJob, PorterJobAdmin)
