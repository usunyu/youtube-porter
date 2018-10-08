# -*- coding: utf-8 -*-
'''
Parsing data from http://api.bilibili.cn/recommend and
creating corresponding PorterJob.
'''

from porter.models import YoutubeAccount

CREATE_ACCOUNTS = [
    {
        'name': 'yportmaster',
        'secret_file': 'secrets/yportmaster.json'
    },
    {
        'name': 'usunyu',
        'secret_file': 'secrets/usunyu.json'
    }
]

for account in CREATE_ACCOUNTS:
    if YoutubeAccount.objects.filter(name=account['name']).exists():
        print('{} existed, skipped...'.format(account['name']))
        continue
    YoutubeAccount(name=account['name'], secret_file=account['secret_file']).save()
    print('{} created.'.format(account['name']))
