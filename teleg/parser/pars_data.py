import datetime
from json import loads
import asyncio
from typing import Awaitable

import aiohttp
from bs4 import BeautifulSoup
import lxml

from .helpers_pars import create_first_data, headers_kuf, headers_av, chunks
from teleg.database import ParsInfo, Users
from teleg.bot.core import bot_
from teleg.bot.keyboard import get_flag_ikb
from teleg.bot.helpers import get_user

import os
from dotenv import load_dotenv


load_dotenv()

# proxy = os.getenv("PROXY")


async def first_pars(url: str, user_id: int, site_name: str, admin=False) -> None:
    headers = headers_kuf
    if site_name != 'kufar':
        headers = headers_av

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    if admin:
        get_user(id_user=user_id, link=url, site_name=site_name)
    mass = []

    parsed = soup.find('script', id='__NEXT_DATA__')
    parsed_text = parsed.text
    parsed_json: dict = loads(parsed_text)

    if site_name == 'kufar':
        ads, __id = parsed_json['props']['initialState']['listing']['ads'], 'ad_id'
    else:
        ads, __id = parsed_json['props']['initialState']['filter']['main']['adverts'], 'id'

    for item in ads:
        mass.append(item[__id])

    create_first_data(user_id, mass, site_name)


async def get_descr_ad(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    return soup.select_one('div.styles_description_content__raCHR').text.replace('\n', '')


async def get_result_parser_kuf(url, user_id, site_name):
    async with aiohttp.ClientSession(headers=headers_kuf) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    parsed = soup.find('script', id='__NEXT_DATA__')
    parsed_text = parsed.text
    parsed_json: dict = loads(parsed_text)
    ads = parsed_json['props']['initialState']['listing']['ads']
    pattern = '%Y-%m-%dT%H:%M:%S'

    result_mass = []
    name, cre, crca, rgd, crg = '', '', '', '', ''
    for ad in ads:
        __id = ad['ad_id']
        _select = ParsInfo.select().where(
            ParsInfo.ad_id == __id,
            ParsInfo.user_id == user_id,
            ParsInfo.site_name == site_name
        )
        if _select.exists():
            break

        time_publish = datetime.datetime.strptime(ad['list_time'][:-1], pattern)
        link_photo = []
        link = ad['ad_link']
        descr = await get_descr_ad(ad['ad_link'])

        city_ = ''
        name_ = ''

        price = 'Договорная' if int(ad['price_usd']) == 0 else ad['price_usd'][:-2]

        for ac_param in ad['account_parameters']:
            try:
                if len(ad['account_parameters']) == 1:
                    name = ac_param['v'].strip()
                else:
                    if ac_param['p'] == 'contact_person':
                        name = ac_param['v'].strip()
            except ValueError:
                name = 'Имя продавца не найдено.'

        for item in ad['ad_parameters']:
            if item['p'] == 'regdate':
                rgd = item['v']
            elif item['p'] == 'cars_engine':
                cre = item['vl']
            elif item['p'] == 'cars_capacity':
                crca = item['vl']
            elif item['p'] == 'cars_gearbox':
                crg = item['vl']
            elif item['pl'] == 'Марка':
                name_ += item['vl']
            elif item['pl'] == 'Модель':
                name_ += f" / {item['vl']}"
            elif item['pl'] == 'Область':
                city_ += item['vl']
            elif item['pl'] == 'Город / Район':
                city_ += f" / {item['vl']}"

        for img in ad['images']:
            link_photo.append(f'https://rms.kufar.by/v1/gallery/{img["path"]}')

        if len(link_photo) == 0:
            link_photo.append(
                'https://avatars.mds.yandex.net/i?id=8f3d7581c4b4cef65478bc2e72c193a7-5233567-images-thumbs&n=13'
            )

        time_publish += datetime.timedelta(hours=3)

        per = ParsInfo.create(user=user_id,
                              ad_id=__id,
                              site_name=site_name,
                              seller=name,
                              link_photo=' '.join(link_photo),
                              link=link,
                              time_publish=time_publish,
                              price_car=price,
                              car_name=name_,
                              city=city_,
                              cre=cre,
                              crca=crca,
                              rgd=rgd,
                              crg=crg,
                              descr=descr,
                              phone=''
                              )

        result_mass.append(per)

    return result_mass


async def get_phone_av(url):
    async with aiohttp.ClientSession(headers=headers_av) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    parsed = soup.find('script', id='__NEXT_DATA__')
    parsed_text = parsed.text
    parsed_json: dict = loads(parsed_text)
    dirty_phone = parsed_json['props']['initialState']['advert']['campaigns'][0]['product']['organization']

    return f"+375{dirty_phone['phones'][0]['phone']['number']}"


async def get_result_parser_av(url, user_id, site_name):
    async with aiohttp.ClientSession(headers=headers_av) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    parsed = soup.find('script', id='__NEXT_DATA__')
    parsed_text = parsed.text
    parsed_json: dict = loads(parsed_text)
    ads = parsed_json['props']['initialState']['filter']['main']['adverts']

    pattern = '%Y-%m-%dT%H:%M:%S'

    result_mass = []
    name, cre, crca, rgd, crg = '', '', '', '', ''
    for ad in ads:
        __id = ad['id']
        _select = ParsInfo.select().where(
            ParsInfo.ad_id == __id,
            ParsInfo.user_id == user_id,
            ParsInfo.site_name == site_name
        )
        if _select.exists():
            break

        name_ = ''
        link_photo = []
        try:
            time_publish = datetime.datetime.strptime(ad['highlightExpiredAt'][:-5], pattern)
        except:
            time_publish = datetime.datetime.strptime(ad['refreshedAt'][:-5], pattern)

        link = ad['publicUrl']
        descr = ad['description']

        city_ = ad['locationName']
        try:
            price = int(ad['price']['usd']['amountFiat'])
        except:
            price = 'Договорная'
        try:
            name = ad['sellerName']
        except ValueError:
            name = 'Имя продавца не найдено.'

        for item in ad['properties']:
            if item['name'] == 'year':
                rgd = item['value']
            elif item['name'] == 'engine_type':
                cre = item['value']
            elif item['name'] == 'engine_capacity':
                crca = item['value']
            elif item['name'] == 'transmission_type':
                crg = item['value']
            elif item['name'] == 'brand':
                name_ += item['value']
            elif item['name'] == 'model':
                name_ += f" / {item['value']}"
            elif item['name'] == 'model':
                name_ += f" / {item['generation']}"

        for img in ad['photos']:
            link_photo.append(f'{img["big"]["url"]}')

        if len(link_photo) == 0:
            link_photo.append(
                'https://avatars.mds.yandex.net/i?id=8f3d7581c4b4cef65478bc2e72c193a7-5233567-images-thumbs&n=13'
            )

        time_publish += datetime.timedelta(hours=3)
        per = ParsInfo.create(user=user_id,
                              ad_id=__id,
                              site_name=site_name,
                              seller=name,
                              link_photo=' '.join(link_photo),
                              link=link,
                              time_publish=time_publish,
                              price_car=price,
                              car_name=name_,
                              city=city_,
                              cre=cre,
                              crca=crca,
                              rgd=rgd,
                              crg=crg,
                              descr=descr,
                              phone=await get_phone_av(link)
                              )
        result_mass.append(per)

    return result_mass


async def send_ads(user_id: int, items: list):
    for item in items:
        text = repr(item)
        all_photos = item.link_photo.split(' ')

        await bot_.send_photo(
            chat_id=user_id,
            photo=all_photos[0],
            caption=text,
            reply_markup=get_flag_ikb(item=item)
        )


async def pars_manager(item: Users, user_id: int):
    data = None

    if item.site_name == 'kufar':
        data = await get_result_parser_kuf(url=item.pars_link, user_id=user_id, site_name='kufar')
    if item.site_name == 'av':
        data = await get_result_parser_av(url=item.pars_link, user_id=user_id, site_name='av')

    if isinstance(data, list) and len(data) >= 1:
        await send_ads(
            user_id=user_id,
            items=data
        )
    await asyncio.sleep(0.5)


async def schedule():
    while True:
        await asyncio.sleep(2)
        select_: list[Users] = Users.select()
        processes: [Awaitable] = []

        for item in select_:
            user_id = item.user_id
            processes.append(pars_manager(item=item, user_id=user_id))

        for items in chunks(processes, 4):
            await asyncio.gather(*items)
