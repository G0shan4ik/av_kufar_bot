import datetime
from json import loads
import asyncio
from random import randint
from typing import Awaitable

import aiohttp
from bs4 import BeautifulSoup
import lxml

from .helpers_pars import create_first_data, headers_kuf, headers_av, chunks, get_delay
from teleg.database import ParsInfo, Users, ObjectsInfo
from teleg.bot.core import bot_, admin_id, user_id_1
from teleg.bot.keyboard import get_flag_ikb, get_obj_ikb
from teleg.bot.helpers import get_user

import os
from dotenv import load_dotenv


load_dotenv()

proxy: list = os.getenv("PROXY").split('$')


async def first_pars(url: str, user_id: int, site_name: str, admin=False, obj=False) -> None:
    headers = headers_kuf
    if site_name != 'kufar':
        headers = headers_av

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    if admin:
        get_user(id_user=user_id, link=url, site_name=site_name, obj=obj)
    mass = []

    if obj:
        all_ads = soup.select('section')[1:]
        for item in all_ads:
            _link: str = item.select_one('a').get('href').split('?')
            mass.append(int(_link[0].split('/')[-1]))
        create_first_data(user_id, mass, site_name, obj=True)
        return

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

async def pars_objects(url, user_id):
    result_mass = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response1:
            soup1 = BeautifulSoup(await response1.text(encoding='utf-8'), 'lxml')

        all_ads = soup1.select('section')[1:]
        for item in all_ads:
            _link: str = item.select_one('a').get('href')

            _select = ObjectsInfo.select().where(
                ObjectsInfo.ad_id == int(_link.split('?')[0].split('/')[-1]),
                ObjectsInfo.user_id == user_id,
                ObjectsInfo.site_name == 'kufar'
            )
            if _select.exists():
                continue
            async with session.get(_link) as response2:
                soup2 = BeautifulSoup(await response2.text(encoding='utf-8'), 'lxml')
            _link_photo: str = soup2.select_one('div.swiper-zoom-container').select_one('img').get('src')
            _time_publish: str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
            _title: str = soup2.select_one('h1').text
            _price: str = soup2.find('span', class_=lambda c: c and c.startswith('styles_main__')).text
            per = ObjectsInfo.create(
                user=user_id,
                ad_id=int(_link.split('?')[0].split('/')[-1]),
                site_name='kufar',
                link_photo=_link_photo,
                link=_link,
                time_publish=_time_publish,
                price=_price,
                title=_title
            )

            result_mass.append(per)
    return result_mass


async def get_descr_ad(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

        return soup.select_one('div.styles_description_content__raCHR').text.replace('\n', '')
    except:
        print(f'\nUrl: {url}\n, Soup: {soup}\n')
        await bot_.send_message(
            chat_id=admin_id,
            text='err'
        )


async def get_result_parser_kuf(url, user_id, site_name):
    async with aiohttp.ClientSession(headers=headers_kuf) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    parsed = soup.find('script', id='__NEXT_DATA__')
    try:
        parsed_text = parsed.text
    except AttributeError:
        await bot_.send_message(
            chat_id=admin_id,
            text=f'{url}'
        )
        print('\n\n', soup, '\n\n')
        await asyncio.sleep(10)
        return
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
            continue

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
            continue

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


async def send_ads(user_id: int, items: list, obj: bool = False):
    for item in items:
        text = repr(item)
        if obj:
            await bot_.send_photo(
                chat_id=user_id,
                photo=item.link_photo,
                caption=text,
                reply_markup=get_obj_ikb(item=item)
            )
        else:
            all_photos = item.link_photo.split(' ')

            await bot_.send_photo(
                chat_id=user_id,
                photo=all_photos[0],
                caption=text,
                reply_markup=get_flag_ikb(item=item)
            )


async def pars_manager(item: Users, user_id: int, obj: bool = False):
    data = None
    if obj and item.site_name == 'kufar':
        data = await pars_objects(url=item.pars_link, user_id=user_id)
    elif item.site_name == 'kufar' and not obj:
        data = await get_result_parser_kuf(url=item.pars_link, user_id=user_id, site_name='kufar')
    elif item.site_name == 'av':
        data = await get_result_parser_av(url=item.pars_link, user_id=user_id, site_name='av')

    if isinstance(data, list) and len(data) >= 1:
        await send_ads(
            user_id=user_id,
            items=data,
            obj=obj
        )
    await asyncio.sleep(0.5)


async def pars_sale_cars(url: str = 'https://auto.kufar.by/l/r~brestskaya-obl/cars?cur=USD&prc=r%3A0%2C2000&sort=lst.d'):
    async with aiohttp.ClientSession(headers=headers_kuf) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(encoding='utf-8'), 'lxml')

    parsed = soup.find('script', id='__NEXT_DATA__')
    try:
        parsed_text = parsed.text
    except AttributeError:
        await bot_.send_message(
            chat_id=admin_id,
            text=f'{url}'
        )
        print('\n\n', soup, '\n\n')
        await asyncio.sleep(10)
        return
    parsed_json: dict = loads(parsed_text)
    ads = parsed_json['props']['initialState']['listing']['ads']
    pattern = '%Y-%m-%dT%H:%M:%S'

    result_mass = []
    name, cre, crca, rgd, crg = '', '', '', '', ''
    for ad in ads:
        __id = ad['ad_id']
        _select = ParsInfo.select().where(
            ParsInfo.ad_id == __id,
            ParsInfo.user_id == admin_id,
            ParsInfo.site_name == 'kufar'
        )
        if _select.exists():
            continue

        key_words, flag = ['срочно', 'Срочно'], False
        descr = await get_descr_ad(ad['ad_link'])
        for wr in key_words:
            if wr in descr:
                flag = True
                break
        if not flag:
            continue

        time_publish = datetime.datetime.strptime(ad['list_time'][:-1], pattern)
        link_photo = []
        link = ad['ad_link']

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

        per = ParsInfo.create(user=admin_id,
                              ad_id=__id,
                              site_name='kufar',
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

        text = f"❗️❗️❗️ СРОЧНОЕ ❗️❗️❗️\n{repr(per)}\n❗️❗️❗️❗️❗️❗️❗️❗️❗️"
        all_photos = per.link_photo.split(' ')

        await bot_.send_photo(
            chat_id=admin_id,
            photo=all_photos[0],
            caption=text,
            reply_markup=get_flag_ikb(item=per)
        )
        await bot_.send_photo(
            chat_id=user_id_1,
            photo=all_photos[0],
            caption=text,
            reply_markup=get_flag_ikb(item=per)
        )

async def schedule():
    while True:
        await asyncio.sleep(2)
        select_: list[Users] = Users.select()
        processes: [Awaitable] = []

        for item in select_:
            user_id = item.user_id
            processes.append(pars_manager(item=item, user_id=user_id, obj=item.obj))

        for items in chunks(processes, 2):
            items.append(pars_sale_cars())
            await asyncio.gather(*items)
            await asyncio.sleep(get_delay())
