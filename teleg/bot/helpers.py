import random
import re
import string
from uuid import uuid4

from teleg.database import Users


def get_unique_id() -> str:
    unique_part_1 = str(uuid4()).split('-')[-1]
    unique_part_2 = str(round(random.uniform(0, 100), 3))
    unique_part_3 = random.choice(string.ascii_letters) + random.choice(string.ascii_letters)
    return unique_part_1 + unique_part_2.replace('.', '') + unique_part_3


def get_user(id_user, link, site_name, obj=False):
    user, _ = Users.get_or_create(
        user_id=id_user,
        unique_id=get_unique_id(),
        pars_link=link,
        site_name=site_name,
        obj=obj
    )
    return user


def add_first_ads_id(id_user, link):
    user, _ = Users.get_or_create(
        user_id=id_user,
        unique_id=get_unique_id(),
        pars_link=link
    )
    return user


def delete_link(user_id, unique_id):
    query = Users.delete().where(Users.user_id == user_id, Users.unique_id == unique_id)
    query.execute()
    return True


def get_links(user_id):
    select_ = Users.select().where(Users.user_id == user_id)
    mass = []
    for item in select_:
        mass.append([item.unique_id, item.site_name, item.pars_link, item.obj])
    return mass


def return_prefix(num: int) -> str:
    if num == 1:
        return '1-го!'
    elif num == 2:
        return '2-ух!'
    elif num == 3 or num == 4:
        return f'{num}-ёх!'
    else:
        return f'{num}-и!'