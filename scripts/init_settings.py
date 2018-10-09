# -*- coding: utf-8 -*-
'''
Create a settings object, all settings will be load from
first object.
'''

from porter.models import Settings

if not Settings.objects.all().first():
    Settings().save()
    print('Settings object created.')
else:
    print('Settings object existed, skipped...')
