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
