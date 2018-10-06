from django.shortcuts import render
from django.conf import settings

# important: schedule_jobs for start schedule jobs, do not remove
if settings.START_JOB:
    from porter import schedulers
