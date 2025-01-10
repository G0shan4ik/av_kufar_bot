from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .core import router_admin
from .keyboard import admin_kb, start_kb, cancel_kb
from teleg.parser.pars_data import first_pars

import os
from aiogram import F
from aiogram.fsm.state import StatesGroup, State


class AddUser(StatesGroup):
    add = State()
    add_car = State()
    add_obj = State()



ADMIN_ID = int(os.getenv('ADMIN_ID'))


@router_admin.message(F.text == 'Отмена')  # exit the state
async def exit_the_state(message: Message, state: FSMContext):
    await message.answer(
        text='Вы вурнулись в главное меню.',
        reply_markup=start_kb(message.from_user.id)
    )
    await state.clear()


@router_admin.message(F.text == "Добавить ссылку для юзера👨‍👩‍‍👦")
async def add_link(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer('Какую ссылку хотите установить', reply_markup=admin_kb())
        await state.set_state(AddUser.add)


@router_admin.message(AddUser.add, F.text == 'Ссылка для авто.' or F.text == 'Ссылка для товара.')
async def send_link(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await message.answer('Пришлите мне вашу ссылку...', reply_markup=cancel_kb())
        if message.text == 'Ссылка для авто.':
            await state.set_state(AddUser.add_car)
        elif message.text == 'Ссылка для товара.':
            await state.set_state(AddUser.add_obj)

@router_admin.message(AddUser.add_car, F.text)
async def add_link_car(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        user_id, url = message.text.split()
        site_name = 'kufar'
        if 'cars.av.by' in url:
            site_name = 'av'
        await first_pars(url, int(user_id), site_name, admin=True)
        await message.answer('Ссылка успешно установлена')

        await state.clear()


@router_admin.message(AddUser.add_obj, F.text)
async def add_link_obj(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        user_id, url = message.text.split()

        await first_pars(url, int(user_id), 'kufar', admin=True, obj=True)
        await message.answer('Ссылка успешно установлена')

        await state.clear()