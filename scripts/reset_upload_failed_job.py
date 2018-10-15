# -*- coding: utf-8 -*-
'''
Reset the porter job with UPLOAD_FAIL status to PENDING status.
'''

from porter.models import PorterJob
from porter.enums import PorterStatus

jobs = PorterJob.objects.filter(status=PorterStatus.UPLOAD_FAIL)
for job in jobs:
    job.status = PorterStatus.PENDING
    job.save(update_fields=['status'])
    print('Reset job {}.'.format(job.id))
