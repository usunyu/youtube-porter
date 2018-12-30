#!/usr/bin/python
import os, subprocess, httplib2
from porter.utils import *
from porter.enums import PorterStatus, PorterThumbnailStatus


TAG = '[YOUTUBE UPLOADER]'

DEFAULT_DESCRIPTION = """{}

喜欢的话不要忘记订阅点赞和分享哦 ^_^
视频来源和原始版权归属原创作者, 影片论点和本频道无关. 本频道致力于视频影片的推广, 学习和传播工作.
如果侵犯了您的权益请留言告知, 本频道会遵照著作权保护法相关规定马上删除影片并且停止分享!
"""

TIKTOK_DESCRIPTION = """喜欢的话不要忘记点赞订阅和分享哦 ❤️
Please give me thumbs up, subscribe and share if you like it 😘
"""

def get_desc_by_account(account):
    if account == get_youtube_yporttiktok_account():
        return TIKTOK_DESCRIPTION
    elif account.name in get_no_copyright_desc_accounts():
        return """{}"""
    else:
        return DEFAULT_DESCRIPTION

def youtube_upload(job):
    video = job.video
    youtube_account = job.youtube_account

    print_log(TAG, 'Start to upload job: ' + str(job.id))
    print_log(TAG, 'Video: ' + video.title)
    print_log(TAG, 'Youtube account: ' + youtube_account.name)

    try:
        # update status to *UPLOADING*
        job.status = PorterStatus.UPLOADING
        job.save(update_fields=['status'])
        print_log(TAG, '******************************************')
        print_log(TAG, '*  Attention! Password may be required!  *')
        print_log(TAG, '******************************************')
        # upload to youtube
        DESC_TEMPLATE = get_desc_by_account(youtube_account)
        video_desc = ''
        if video.description:
            video_desc = video.description
        upload_command = 'sudo youtube-upload --title="{}" --description="{}" --category="{}" --tags="{}" --client-secrets="{}" --credentials-file="{}"'.format(
            video.title,
            DESC_TEMPLATE.format(video_desc),
            video.category,
            video.print_tags(),
            youtube_account.secret_file,
            youtube_account.credentials_file
        )
        if job.playlist and youtube_account.name not in get_no_playlist_accounts():
            upload_command = upload_command + ' --playlist="' + job.playlist + '"'
        if youtube_account.name in get_private_video_accounts():
            upload_command += ' --privacy private'
        upload_command = upload_command + ' ' + job.video_file
        # print_log(TAG, 'Run command: ' + upload_command)
        output = subprocess.check_output(upload_command, shell=True)
        youtube_id = output.decode("utf-8").strip()
        if 'Enter verification code: ' in youtube_id:
            youtube_id = youtube_id.replace('Enter verification code: ', '')
        job.youtube_id = youtube_id
        job.upload_at = get_current_time()
        # update status to *SUCCESS*
        job.status = PorterStatus.SUCCESS
        job.save(update_fields=['youtube_id', 'status', 'upload_at'])
        youtube_account.upload_quota = youtube_account.upload_quota - 1
        youtube_account.save(update_fields=['upload_quota'])

    except:
        print_exception(TAG, 'Upload video: ' + video.title + ' exception!')
        print_log(TAG, 'Upload video: ' + video.title + ' exception!')
        # TODO, check exception upload limit or playlist limit
        # if playlist limit, upload status still should be true
        # update status to *UPLOAD_FAIL*
        job.status = PorterStatus.UPLOAD_FAIL
        job.save(update_fields=['status'])
        # set account quota 0 to avoid continue upload fail
        youtube_account.upload_quota = 0
        youtube_account.save(update_fields=['upload_quota'])
    # clean video file
    clean_file(TAG, job.video_file)


from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# https://github.com/youtube/api-samples/blob/master/python/upload_thumbnail.py
#
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
# CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0
To make this sample run you will need to populate the client_secrets.json file
found at:
    {}
with information from the Cloud Console
https://cloud.google.com/console
For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
"""

def get_authenticated_service(account):
    flow = flow_from_clientsecrets(account.secret_file,
                                   scope=YOUTUBE_READ_WRITE_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE.format(account.secret_file))

    storage = Storage(account.credentials_file)
    credentials = storage.get()

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))

# Call the API's thumbnails.set method to upload the thumbnail image and
# associate it with the appropriate video.
def upload_thumbnail(youtube, video_id, file):
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=file).execute()


def youtube_thumbnail_upload(job):
    if not job.thumbnail_file:
        print_log(TAG, 'Thumbnail file too small, skipped...')
        return

    if not os.path.exists(job.thumbnail_file):
        print_log(TAG, 'Thumbnail file not found!')
        return

    if not job.thumbnail_status == PorterThumbnailStatus.DEFAULT:
        print_log(TAG, 'Thumbnail not need updated, skipped...')
        clean_file(TAG, job.thumbnail_file)
        return

    if not job.youtube_id:
        print_log(TAG, 'No youtube id found, skipped...')
        clean_file(TAG, job.thumbnail_file)
        return

    try:
        youtube = get_authenticated_service(job.youtube_account)
        upload_thumbnail(youtube, job.youtube_id, job.thumbnail_file)
    # except HttpError as e:
    #     job.thumbnail_status = PorterThumbnailStatus.FAILED
    #     job.save(update_fields=['thumbnail_status'])
    #     print_log(TAG, 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    except:
        job.thumbnail_status = PorterThumbnailStatus.FAILED
        job.save(update_fields=['thumbnail_status'])
        print_exception(TAG, 'Upload thumbnail ' + job.thumbnail_file + ' exception!')
        print_log(TAG, 'Upload thumbnail ' + job.thumbnail_file + ' exception!')
        # clean thumbnail file
        clean_file(TAG, job.thumbnail_file)
        return

    job.thumbnail_status = PorterThumbnailStatus.UPDATED
    job.save(update_fields=['thumbnail_status'])
    print_log(TAG, 'The custom thumbnail was successfully set.')

    # clean thumbnail file
    clean_file(TAG, job.thumbnail_file)
