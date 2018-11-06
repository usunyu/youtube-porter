from porter.uploaders.youtube_uploader import youtube_upload


TAG = '[UPLOADER]'

def upload(job):

    if job.youtube_account:
        youtube_upload(job)
    # TODO, support upload to other account
