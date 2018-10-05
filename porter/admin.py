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
            return format_html('<a href="/admin/porter/video/{}/" target="_blank">{}</a>'.format(
                video.id, video.id
            ))
        return '-'

    def youtube_link(self, obj):
        if obj.youtube_id:
            return format_html('<a href="https://www.youtube.com/watch?v={}/" target="_blank">{}</a>'.format(
                obj.youtube_id, obj.youtube_id
            ))
        return '-'

    video_detail.short_description = 'VID'
    youtube_link.short_description = 'Youtube Link'

    list_display = [
        'id',
        'status',
        'created_at',
        'video_url',
        'video_source',
        'video',
        'video_detail',
        # 'video_file',
        'download_at',
        'youtube_account',
        'youtube_link',
        'upload_at'
    ]

    readonly_fields = [
        'video',
        'youtube_id',
        'video_file',
        'download_at',
        'upload_at'
    ]

admin.site.register(PorterJob, PorterJobAdmin)
