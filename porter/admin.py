from django.contrib import admin
from django.utils.html import format_html
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
        'print_tags'
    ]

admin.site.register(Video, VideoAdmin)

class PorterJobAdmin(admin.ModelAdmin):

    def video_detail(self, obj):
        video = Video.objects.filter(url=obj.video_url).first()
        if video:
            return format_html('<a href="/admin/porter/video/{}/" target="_blank">{}</a>'.format(video.id, video.id))
        return 'None'

    video_detail.short_description = 'vid'

    list_display = [
        'id',
        'video_url',
        'video_source',
        'video',
        'video_detail',
        'video_file',
        'youtube_account',
        'status'
    ]

    readonly_fields = ['video', 'video_file']

admin.site.register(PorterJob, PorterJobAdmin)
