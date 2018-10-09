from django.shortcuts import render
from django.conf import settings

if settings.IMPORT_SCHEDULE:
    from porter import schedulers
