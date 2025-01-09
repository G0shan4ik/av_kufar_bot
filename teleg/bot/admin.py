from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .core import router_admin
from teleg.parser.pars_data import first_pars

import os
from aiogram import F
from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    add = State()


ADMIN_ID = int(os.getenv('ADMIN_ID'))


@router_admin.message(F.text == "Добавить юзера👨‍👩‍👦‍👦")
async def add_link(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer('Wait...')
        await state.set_state(AddUser.add)


@router_admin.message(AddUser.add, F.text)
async def add_link(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        user_id, url = message.text.split()
        site_name = 'kufar'
        if 'cars.av.by' in url:
            site_name = 'av'
        await first_pars(url, int(user_id), site_name, admin=True)
        await message.answer('added')

        await state.clear()