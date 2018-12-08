import requests, json, re, time
from django.db.models import Q
from porter.utils import *
from porter.models import PorterJob, Video, YoutubeAccount
from porter.enums import VideoSource, PorterStatus, PorterJobType


TAG = '[KUAIYINSHI FETCHER]'

KUAIYINSHI_CHANNEL_API = 'https://kuaiyinshi.com/api/videos/?source={}&user_id={}&page={}'
KUAIYINSHI_RECOMMEND_API = 'https://kuaiyinshi.com/api/hot/videos/?source={}&page={}&st={}'

DELAY_INTERVAL = 5

# kuaiyinshi user channel video link has encrpted
def douyin_channel_fetch_DEPRECATED(job):
    channel_url = job.url
    user_id = re.findall('([0-9]+)', channel_url)[0]
    response = requests.get(KUAIYINSHI_CHANNEL_API.format('dou-yin', user_id, 1))
    payload = json.loads(response.text)
    account = job.youtube_account
    if payload['code'] != 200:
        print_log(TAG, 'Fetch channel ' + channel_url + ' failed!')
        return
    video_list = []
    # this channel already fetched before
    if job.last_fetched_at:
        # only fetch first page
        vlist = json.loads(response.text)['data']
        vlist.reverse()
        video_list = vlist
    else: # this channel not fetched before
        page = 1
        while True:
            api_url = KUAIYINSHI_CHANNEL_API.format('dou-yin', user_id, page)
            res = requests.get(api_url)
            if res['code'] != 200:
                break
            vlist = json.loads(res.text)['data']
            vlist.reverse()
            video_list.extend(vlist)
            page += 1
            time.sleep(DELAY_INTERVAL)

    # create porter job
    # did not tested
    added_jobs = 0
    for video in video_list:
        download_url = 'http:' + record['video_url']
        if PorterJob.objects.filter(
            Q(download_url=download_url) &
            Q(youtube_account=account)
        ).exists():
            continue
        user_name = record['nickname']
        title = record['desc']
        statistics = record['statistics']
        likes = statistics['zan']
        comments = statistics['comment']
        shares = statistics['share']
        thumbnail_url = 'http:' + record['video_img']
        video = Video(url='-', title='@' + user_name + ' ' + title)
        video.save()
        PorterJob(video_url='-',
                  download_url=download_url,
                  thumbnail_url=thumbnail_url,
                  youtube_account=account,
                  video_source=VideoSource.DOUYIN,
                  video=video,
                  status=PorterStatus.PENDING_REVIEW,
                  type=PorterJobType.MERGE,
                  likes=likes,
                  comments=comments,
                  shares=shares).save()
        added_jobs = added_jobs + 1
    print_log(TAG, 'Create {} new jobs from channel {}'.format(added_jobs, job.name))

    # update last fetched time
    job.last_fetched_at = get_current_time()
    job.save(update_fields=['last_fetched_at'])


def douyin_recommend_fetch():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'}
    response = requests.get(KUAIYINSHI_RECOMMEND_API.format('dou-yin', 1, 'day'), headers=headers)
    payload = json.loads(response.text)

    if payload['code'] == 200:
        data = payload['data']

        # upload to yporttiktok account
        account = get_youtube_yporttiktok_account()
        added_jobs = 0
        for record in data:
            download_url = 'http:' + record['video_url']
            if PorterJob.objects.filter(
                Q(download_url=download_url) &
                Q(youtube_account=account)
            ).exists():
                continue
            user_name = record['nickname']
            title = record['desc']
            statistics = record['statistics']
            likes = statistics['zan']
            comments = statistics['comment']
            shares = statistics['share']
            thumbnail_url = 'http:' + record['video_img']
            video = Video(url='-', title='@' + user_name + ' ' + title)
            video.save()
            PorterJob(video_url='-',
                      download_url=download_url,
                      thumbnail_url=thumbnail_url,
                      youtube_account=account,
                      video_source=VideoSource.DOUYIN,
                      video=video,
                      status=PorterStatus.PENDING_REVIEW,
                      type=PorterJobType.MERGE,
                      likes=likes,
                      comments=comments,
                      shares=shares).save()
            added_jobs = added_jobs + 1
        print_log(TAG, 'Create {} new jobs from Douyin'.format(added_jobs))
