import re
from django.contrib import admin
from django.utils.html import format_html
from porter.models import *
from porter.enums import VideoSource

admin.site.register(YoutubeAccount)
admin.site.register(VideoTag)

class VideoAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'url',
        'title',
        'description',
        'print_tags'
    ]

admin.site.register(Video, VideoAdmin)

class PorterJobAdmin(admin.ModelAdmin):

    def video_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>'.format(
            obj.video_url, obj.video_url
        ))

    def video_detail(self, obj):
        video = Video.objects.filter(url=obj.video_url).first()
        if video:
            return format_html('<a href="/admin/porter/video/{}" target="_blank">{}</a>'.format(
                video.id, video.id
            ))
        return '-'

    def youtube_link(self, obj):
        if obj.youtube_id:
            return format_html('<a href="https://www.youtube.com/watch?v={}" target="_blank">{}</a>'.format(
                obj.youtube_id, obj.youtube_id
            ))
        return '-'

    def api_link(self, obj):
        if obj.video_source == VideoSource.BILIBILI:
            video_id = re.findall('.*av([0-9]+)', obj.video_url)[0]
            return format_html('<a href="https://www.kanbilibili.com/api/video/{}" target="_blank">{}</a>'.format(
                video_id, video_id
            ))
        return '-'

    video_link.short_description = 'Link'
    video_detail.short_description = 'VID'
    api_link.short_description = 'API Link'
    youtube_link.short_description = 'Youtube Link'

    list_display = [
        'id',
        'status',
        'created_at',
        'video_link',
        'video_source',
        'api_link',
        'video',
        'video_detail',
        'video_file',
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
