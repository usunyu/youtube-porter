# -*- coding: utf-8 -*-
'''
Set the target porter jobs to STOP status.
'''

from django.db.models import Q
from porter.utils import *
from porter.models import PorterJob, YoutubeAccount
from porter.enums import PorterStatus

account = get_youtube_yportcomment_account()

jobs = PorterJob.objects.filter(
    # Q(status=PorterStatus.PENDING) &
    Q(youtube_account=account) &
    Q(playlist='猫叔说电影')
    )
for job in jobs:
    job.status = PorterStatus.STOP
    job.save(update_fields=['status'])
    print('Stop job {}.'.format(job.id))
