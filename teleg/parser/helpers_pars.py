from datetime import datetime, timezone, timedelta

from teleg.database import ParsInfo, ObjectsInfo


def create_first_data(user_id, data, site_name, obj=False):
    for _id in data:
        if obj:
            ObjectsInfo.get_or_create(
                user_id=user_id,
                ad_id=_id,
                site_name=site_name
            )
        else:
            ParsInfo.get_or_create(
                user_id=user_id,
                ad_id=_id,
                site_name=site_name
            )


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


headers_kuf = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/112.0.0.0 YaBrowser/23.5.2.625 Yowser/2.5 Safari/537.36'
}

headers_av = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36",
    'Accept': '*/*'
}


def get_correct_current_time():
    zone = timezone(timedelta(hours=3))
    now = datetime.now(zone)
    return datetime.strptime(now.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")


def get_delay() -> int:
    tm = get_correct_current_time().time()
    current_time = datetime.strptime(tm.strftime("%H:%M"), "%H:%M").time()
    delay = 10

    morning_time = datetime.strptime("07:00", "%H:%M").time()
    morning_time2 = datetime.strptime("11:00", "%H:%M").time()

    day_time = datetime.strptime("13:00", "%H:%M").time()

    evening_time = datetime.strptime("18:00", "%H:%M").time()
    evening_time2 = datetime.strptime("23:59", "%H:%M").time()

    night_time = datetime.strptime("00:00", "%H:%M").time()

    if morning_time <= current_time <= morning_time2:
        delay = 20
    elif morning_time2 <= current_time <= day_time:
        delay = 12
    elif day_time <= current_time <= evening_time:
        delay = 25
    elif evening_time <= current_time <= evening_time2:
        delay = 35
    elif night_time <= current_time <= morning_time:
        delay = 100

    return delay