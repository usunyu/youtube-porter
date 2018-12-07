# -*- coding: utf-8 -*-
'''
Create Youtube accounts by scripts.
'''

from porter.models import YoutubeAccount

CREATE_ACCOUNTS = [
    {
        'name': 'yportmaster',
        'secret_file': 'secrets/yportmaster.json'
        'secret_file': 'credentials/yportmaster.json'
    },
    {
        'name': 'usunyu',
        'secret_file': 'secrets/usunyu.json'
        'secret_file': 'credentials/usunyu.json'
    }
]

for account in CREATE_ACCOUNTS:
    if YoutubeAccount.objects.filter(name=account['name']).exists():
        print('{} existed, skipped...'.format(account['name']))
        continue
    YoutubeAccount(name=account['name'], secret_file=account['secret_file']).save()
    print('{} created.'.format(account['name']))
