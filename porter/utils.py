from datetime import datetime, timedelta, timezone


def print_log(tag, msg):
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    # bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    us_dt = utc_dt.astimezone(timezone(timedelta(hours=-7)))
    print(tag, us_dt.strftime('%Y-%m-%d %H:%M:%S'), msg)


def get_time_str():
    return datetime.now().strftime('%Y-%m-%d %H-%M-%S')
