import requests
from porter.utils import *


TAG = '[URL DOWNLOADER]'

CHUNK_SIZE = 1024

def url_download(url):
    try:
        response = requests.get(url, headers=get_client_headers(), stream=True)
        total_size = int(response.headers['content-length'])
        format = response.headers['Content-Type']
        filename = get_random_16_code()
        if format == 'video/mp4':
            filename = filename + '.mp4'
        elif format == 'video/x-flv':
            filename = filename + '.flv'
        elif format == 'image/jpeg':
            filename = filename + '.jpg'
        elif format == 'image/png':
            filename = filename + '.png'
        else:
            print_log(TAG, 'Unknown content type!')
            return None
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
    except:
        print_exception(TAG, 'Url download exception!')
        return None
