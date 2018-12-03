from django.shortcuts import render
from django.conf import settings

# start schedulers
if settings.IMPORT_SCHEDULE:
    from porter import schedulers
