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

Temporary fix bilibili-get download [issue](https://github.com/kamikat/bilibili-get/issues/18):
```
$ git clone https://github.com/kamikat/bilibili-get
$ cd libs/bilibili-get/bin/
$ npm i
```

4. Update sqlite3 db permission:
```
$ chmod 666 db.sqlite3
```

5. Run server:
```
$ python manage.py runserver
```

### Add YouTube Account:

1. Download secrets file `secrets/xxxxxx.json` and upload it to server.

2. Update account settings in `utils.py`:
```
def get_no_playlist_accounts():
    ...

def get_no_copyright_desc_accounts():
    ...

def get_youtube_quota_settings():
    ...

def get_youtube_account_order():
    ...
```

3. Add `YoutubeAccount` record.

4. Create an empty credentials file `credentials/xxxxxx.json` from server:
```
$ sudo touch credentials/xxxxxx.json
```

5. Run upload job and enter correct code from browser.

### Deployment:

1. Attach to screen:
```
$ screen -r
```

2. Run server:
```
$ python manage.py runserver --insecure 0.0.0.0:9652
```

### Initial Settings:
```
$ python manage.py shell < scripts/init_settings.py
```
