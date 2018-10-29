import re
from django.contrib import admin
from django.utils.html import format_html
from porter.models import *
from porter.enums import VideoSource

class YoutubeAccountAdmin(admin.ModelAdmin):

    def channel_link(self, obj):
        if obj.channel:
            return format_html('<a href="{}" target="_blank">{}</a>'.format(
                obj.channel, obj.channel
            ))
        return '-'

    channel_link.short_description = 'Channel Link'

    list_display = [
        'id',
        'name',
        'secret_file',
        'credentials_file',
        'upload_quota',
        'description',
        'channel_link',
        'created_at'
    ]

admin.site.register(YoutubeAccount, YoutubeAccountAdmin)

class VideoTagAdmin(admin.ModelAdmin):

    list_display = [
        'id',
        'name',
        'created_at'
    ]

admin.site.register(VideoTag, VideoTagAdmin)

class VideoAdmin(admin.ModelAdmin):

    def url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>'.format(
            obj.url, obj.url
        ))

    url_link.short_description = 'Url'

    list_display = [
        'id',
        'url_link',
        'title',
        'description',
        'print_tags'
    ]

admin.site.register(Video, VideoAdmin)

class ChannelJobAdmin(admin.ModelAdmin):

    def url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>'.format(
            obj.url, obj.url
        ))

    url_link.short_description = 'Url'

    list_display = [
        'id',
        'url_link',
        'name',
        'video_source',
        'youtube_account',
        'last_fetched_at',
        'created_at'
    ]

    readonly_fields = [
        'last_fetched_at'
    ]

admin.site.register(ChannelJob, ChannelJobAdmin)

class PorterJobAdmin(admin.ModelAdmin):

    def video_link(self, obj):
        if obj.video_url == '-':
            if obj.download_url:
                return format_html('<a href="{}" target="_blank">{}</a>'.format(
                    obj.download_url, 'Download Link'
                ))
            return '-'
        return format_html('<a href="{}" target="_blank">{}</a>'.format(
            obj.video_url, obj.video_url
        ))

    def video_detail(self, obj):
        if obj.video:
            return format_html('<a href="/admin/porter/video/{}" target="_blank">{}</a>'.format(
                obj.video.id, obj.video.id
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
        'playlist',
        'type',
        'part',
        'retried',
        'upload_at',
        'views',
        'likes',
        'comments',
        'shares'
    ]

    list_filter = [
        'status',
        'video_source',
        'youtube_account'
    ]

    readonly_fields = [
        'download_url',
        'video',
        'youtube_id',
        'video_file',
        'retried',
        'download_at',
        'upload_at',
        'views',
        'likes',
        'comments',
        'shares'
    ]

admin.site.register(PorterJob, PorterJobAdmin)

class SettingsAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'start_download_job',
        'start_upload_job',
        'start_channel_job',
        'start_bilibili_recommend_job',
        'start_reset_quota_job',
    ]

admin.site.register(Settings, SettingsAdmin)
