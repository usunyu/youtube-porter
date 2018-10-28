import requests
from porter.utils import *


TAG = '[URL DOWNLOADER]'

CHUNK_SIZE = 1024

def url_download(url):
    try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
        response = requests.get(url, headers=headers, stream=True)
        total_size = int(response.headers['content-length'])
        format = response.headers['Content-Type']
        filename = get_time_str()
        if format=='video/mp4':
            filename = filename + '.mp4'
        else:
            filename = filename + '.flv'
        file = open(filename, 'wb')
        print_log(TAG, 'Start downloading...')
        download_size = 0
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                file.write(chunk)
                # file.flush()
            download_size = download_size + CHUNK_SIZE
            end = '\r'
            if download_size > total_size:
                download_size = total_size
                end = '\r\n'
            print(TAG, 'Download progress: {:.0%}'.format(float(download_size) / total_size), end=end, flush=True),
        file.close()
        print_log(TAG, 'Download finish!')
        return filename
    except Exception as e:
        print_log(TAG, 'Unknown error during url download!')
        print_log(TAG, str(e))
        return None
