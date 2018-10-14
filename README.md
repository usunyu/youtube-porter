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

3. Install [bilibili-get](https://github.com/kamikat/bilibili-get):
```
$ npm install -g bilibili-get

$ brew install ffmpeg aria2
# or in unix
$ sudo apt-get install ffmpeg aria2
```

3. Run server:
```
$ python manage.py runserver
```

### Deployment:

1. Attach to screen:
```
$ screen -r
```

2. Run server:
```
$ python manage.py runserver --insecure 0.0.0.0:9346
```

### External Scripts:
1. Init settings:
```
$ python manage.py shell < scripts/init_settings.py
```

2. Init youtube accounts:
```
$ python manage.py shell < scripts/init_youtube_account.py
```

3. Init bilibili recommend jobs:
```
$ python manage.py shell < scripts/init_bilibili_recommend.py
```

### YouTube Channel:
1. YPort Master:

https://www.youtube.com/channel/UC-EXdAi5baz7XGNjuoJWwmQ
