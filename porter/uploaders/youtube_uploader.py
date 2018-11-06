import os, subprocess
from porter.utils import *
from porter.enums import PorterStatus


TAG = '[YOUTUBE UPLOADER]'

VIDEO_DESCRIPTION = """{}

This video is from (视频来源, 请支持原作者): {}

All videos are from online resources. If you find a video that infringes on your rights, please contact yportmaster@gmail.com to delete the video.
If you like this video, please like, comment and subscribe. Thank you!
(所有视频均来自网络资源, 如果侵犯了您的权益请联系yportmaster@gmail.com删除视频.
如果您喜欢此视频, 请点赞, 留言, 订阅. 非常感谢!)
"""

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
        upload_command = 'sudo youtube-upload --title="{}" --description="{}" --category="{}" --tags="{}" --client-secrets="{}" --credentials-file="{}"'.format(
            video.title,
            VIDEO_DESCRIPTION.format(video.description, video.url),
            video.category,
            video.print_tags(),
            youtube_account.secret_file,
            youtube_account.credentials_file
        )
        if job.playlist:
            upload_command = upload_command + ' --playlist="' + job.playlist + '"'
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

    except Exception as e:
        print_log(TAG, 'Failed to upload video: ' + video.title)
        print_log(TAG, str(e))
        # TODO, check exception upload limit or playlist limit
        # if playlist limit, upload status still should be true
        # update status to *UPLOAD_FAIL*
        job.status = PorterStatus.UPLOAD_FAIL
        job.save(update_fields=['status'])
        # set account quota 0 to avoid continue upload fail
        youtube_account.upload_quota = 0
        youtube_account.save(update_fields=['upload_quota'])
    # clean video file
    try:
        os.remove(job.video_file)
        print_log(TAG, 'Deleted video: ' + job.video_file)
    except Exception as e:
        print_log(TAG, 'Failed to delete video: ' + job.video_file)
        print_log(TAG, str(e))
