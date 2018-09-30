from django.contrib import admin
from porter.models import *

admin.site.register(YoutubeAccount)
admin.site.register(VideoTag)
admin.site.register(Video)

class PorterJobAdmin(admin.ModelAdmin):
    # fields = [
    #     'video_url',
    #     'video_source',
    #     'youtube_account'
    # ]
    readonly_fields = ['status']

admin.site.register(PorterJob, PorterJobAdmin)
