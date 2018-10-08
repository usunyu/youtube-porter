# youtube-porter
Automate upload video to YouTube from any sources

### Get Started:

1. Install required packages:
```
$ pip install -r requirements.txt
```

2. Install [youtube-upload](https://github.com/tokland/youtube-upload):
```
$ sudo pip install --upgrade google-api-python-client oauth2client progressbar2

$ cd libs/youtube-upload
$ sudo python setup.py install
```

3. Run Server:
```
$ python manage.py runserver
```

### External Scripts:
1. Existed in ```scripts``` folder.

2. Run script (e.g. ```scripts/bilibili_recommend_import.py```):
```
$ python manage.py shell < scripts/bilibili_recommend_import.py
```
