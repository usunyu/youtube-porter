from porter.uploaders.youtube_uploader import youtube_upload, youtube_thumbnail_upload


TAG = '[UPLOADER]'

def upload(job):

    if job.youtube_account:
        youtube_upload(job)
        youtube_thumbnail_upload(job)

    # TODO, support upload to other account
