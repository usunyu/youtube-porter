from porter.utils import *
from porter.enums import PorterStatus
from porter.models import YoutubeAccount

YOUTUBE_UPLOAD_QUOTA = 90
YOUTUBE_UPLOAD_TIME_INTERVAL = 24 * 60 * 60

accounts = YoutubeAccount.objects.all()
for account in accounts:
    if account.upload_quota > 0:
        continue
    # OPTIMIZE, use last 99 job upload time
    last_success_job = account.porter_jobs.filter(status=PorterStatus.SUCCESS).reverse().first()
    should_reset = False
    if last_success_job:
        interval = get_current_time() - last_success_job.upload_at
        if interval.total_seconds() > YOUTUBE_UPLOAD_TIME_INTERVAL:
            should_reset = True
    else:
        should_reset = True
    if should_reset:
        account.upload_quota = YOUTUBE_UPLOAD_QUOTA
        account.save(update_fields=['upload_quota'])
        print('Reset quota for account: ' + account.name)
